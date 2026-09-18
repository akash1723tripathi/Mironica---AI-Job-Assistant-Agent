"""
Single command entrypoint for daily collection, scoring, delivery and state.
Merges seed & generated sources dynamically, executes all collectors,
evaluates jobs, generates data/reports/quality_report.md, and delivers digests to Telegram.
"""

from __future__ import annotations

import sys
import json
import argparse
import logging
from collections import Counter
from pathlib import Path

# Ensure repository root in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from src.collectors import ats, career_pages, linkedin_jobs, linkedin_posts, workday, yc, zoho_recruit
from src.notifications.telegram import send_digest
from src.processing.dedupe import dedupe
from src.processing.email_finder import discover
from src.processing.eligibility import evaluate
from src.processing.normalize import normalize, utc_now
from src.processing.state import filter_unsent, mark_sent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_pipeline")

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
REPORTS = DATA / "reports"
STATE = DATA / "state" / "sent_jobs.json"


def load_json(path: Path, default: object = None) -> object:
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def merge_sources() -> dict:
    """Merge config/sources.seed.json and config/sources.generated.json dynamically."""
    seed = load_json(ROOT / "config" / "sources.seed.json", {})
    generated = load_json(ROOT / "config" / "sources.generated.json", {})

    merged = dict(seed)

    # Merge ATS boards
    seed_ats = seed.get("ats_boards", [])
    gen_ats = generated.get("ats_boards", [])
    seen_ats = {(b.get("company"), b.get("platform")) for b in seed_ats}
    
    combined_ats = list(seed_ats)
    for b in gen_ats:
        key = (b.get("company"), b.get("platform"))
        if key not in seen_ats:
            seen_ats.add(key)
            combined_ats.append(b)
    merged["ats_boards"] = combined_ats

    # Merge Workday
    seed_wd = seed.get("workday", [])
    gen_wd = generated.get("workday", [])
    seen_wd = {(b.get("company"), b.get("platform")) for b in seed_wd}
    
    combined_wd = list(seed_wd)
    for b in gen_wd:
        key = (b.get("company"), b.get("platform"))
        if key not in seen_wd:
            seen_wd.add(key)
            combined_wd.append(b)
    merged["workday"] = combined_wd

    return merged


def source_status() -> dict:
    return {
        "attempted": True,
        "succeeded": False,
        "records_found": 0,
        "records_accepted": 0,
        "records_rejected": 0,
        "error": ""
    }


def run_source(name: str, runner, report: dict) -> list[dict]:
    status = report["sources"][name]
    try:
        result = runner()
        records, failures = result if isinstance(result, tuple) else (result, [])
        status.update(
            succeeded=not failures or bool(records),
            records_found=len(records),
            error="; ".join(failures[:3]) if failures else ""
        )
        if failures and not records:
            report["failed_sources"].append(name)
        return records
    except Exception as exc:
        status["error"] = str(exc)
        report["failed_sources"].append(name)
        return []


def generate_quality_report(
    raw_jobs: list[dict],
    unique_jobs: list[dict],
    evaluated_jobs: list[dict],
    qualified_jobs: list[dict],
    run_report: dict
) -> str:
    total_raw = len(raw_jobs)
    total_unique = len(unique_jobs)
    duplicate_rate = round(((total_raw - total_unique) / total_raw * 100), 1) if total_raw > 0 else 0.0
    
    scores = [j["score"] for j in qualified_jobs]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Source breakdown
    source_counts = Counter(j.get("source", "unknown") for j in raw_jobs)

    # Rejection breakdown
    reasons = Counter(j.get("reject_reason") for j in evaluated_jobs if j.get("reject_reason"))
    senior_removed = sum(cnt for reason, cnt in reasons.items() if "seniority" in reason or "3+" in reason)
    entry_jobs = sum(1 for j in evaluated_jobs if any(k in f"{j.get('title','')} {j.get('description','')}".lower() for k in ("intern", "fresher", "associate", "entry")))

    # Registry health summary
    registry_report = load_json(REPORTS / "registry_report.json", {})
    reg_valid = registry_report.get("valid_boards", 0)
    reg_scanned = registry_report.get("companies_scanned", 0)

    md = [
        "# AI Job Assistant — Quality Metrics Report",
        f"**Generated At**: `{utc_now()}`",
        "",
        "## Summary Metrics",
        "| Metric | Value | Target Threshold |",
        "|---|---|---|",
        f"| **Raw Jobs Collected** | **{total_raw}** | 200+ |",
        f"| **Unique Jobs (Post-Dedupe)** | **{total_unique}** | — |",
        f"| **Duplicate Rate** | **{duplicate_rate}%** | < 50% |",
        f"| **Qualified Jobs (Score >= 50)** | **{len(qualified_jobs)}** | 10+ |",
        f"| **Average Match Score** | **{avg_score}%** | >= 50% |",
        f"| **Entry-Level Opportunities** | **{entry_jobs}** | — |",
        f"| **Senior Jobs Filtered** | **{senior_removed}** | — |",
        "",
        "## Source Contribution Breakdown",
        "| Source | Raw Collected | Contribution |",
        "|---|---|---|"
    ]

    for src, count in source_counts.most_common():
        pct = round((count / total_raw * 100), 1) if total_raw > 0 else 0.0
        md.append(f"| `{src}` | {count} | {pct}% |")

    md.extend([
        "",
        "## Top Rejection Reasons",
        "| Reason | Count |",
        "|---|---|"
    ])

    for reason, count in reasons.most_common(5):
        md.append(f"| {reason} | {count} |")

    md.extend([
        "",
        "## Registry Health Summary",
        f"- **ATS Companies Validated**: {reg_valid} / {reg_scanned} ({round(reg_valid/reg_scanned*100, 1) if reg_scanned else 0}%)",
        f"- **Dead Boards Detected**: {registry_report.get('dead_boards', 0)}",
        f"- **Provider Breakdown**: {json.dumps(registry_report.get('provider_wise_counts', {}))}",
        ""
    ])

    content = "\n".join(md)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "quality_report.md").write_text(content, encoding="utf-8")
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily AI Job Assistant pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Collect and write output without Telegram/state mutation")
    args = parser.parse_args()

    for directory in (RAW, PROCESSED, REPORTS, STATE.parent):
        directory.mkdir(parents=True, exist_ok=True)

    profile = load_json(ROOT / "config" / "profile.json", {"minimum_score": 50})
    merged_sources = merge_sources()
    search = load_json(ROOT / "config" / "search.json", {})

    names = ("linkedin_jobs", "linkedin_posts", "yc", "greenhouse", "lever", "ashby", "workday", "zoho", "career_pages")
    report = {
        "timestamp": utc_now(),
        "sources": {name: source_status() for name in names},
        "total_collected": 0,
        "after_hard_filter": 0,
        "after_scoring": 0,
        "after_dedupe": 0,
        "final_count": 0,
        "failed_sources": []
    }

    all_jobs = []

    # 1. LinkedIn Jobs & Posts
    linkedin_cfg = merged_sources.get("linkedin", {"enabled": True})
    if linkedin_cfg.get("enabled"):
        jobs = run_source(
            "linkedin_jobs",
            lambda: linkedin_jobs.collect(
                search,
                linkedin_cfg.get("max_jobs_per_query", 20),
                linkedin_cfg.get("max_queries_per_run", 18)
            ),
            report
        )
        enriched, warning = linkedin_jobs.enrich(jobs, linkedin_cfg.get("max_enrichment", 20))
        all_jobs.extend(enriched)

        posts = run_source(
            "linkedin_posts",
            lambda: linkedin_posts.collect(
                linkedin_cfg.get("max_posts_per_query", 15),
                linkedin_cfg.get("max_post_queries_per_run", 10)
            ),
            report
        )
        all_jobs.extend(posts)

    # 2. YC Collector
    yc_cfg = merged_sources.get("yc", {"enabled": True})
    if yc_cfg.get("enabled"):
        all_jobs.extend(run_source("yc", lambda: yc.collect(yc_cfg.get("url", "https://www.workatastartup.com/jobs")), report))

    # 3. ATS Boards (Greenhouse, Lever, Ashby)
    ats_boards = merged_sources.get("ats_boards", [])
    for platform in ("greenhouse", "lever", "ashby"):
        all_jobs.extend(run_source(platform, lambda p=platform: ats.collect(ats_boards, p), report))

    # 4. Workday, Zoho, Career Pages
    all_jobs.extend(run_source("workday", lambda: workday.collect(merged_sources.get("workday", [])), report))
    all_jobs.extend(run_source("zoho", lambda: zoho_recruit.collect(merged_sources.get("zoho_recruit", [])), report))
    all_jobs.extend(run_source("career_pages", lambda: career_pages.collect(merged_sources.get("career_pages", [])), report))

    # Normalize raw jobs
    normalized = [normalize(job) for job in all_jobs]
    report["total_collected"] = len(normalized)
    (RAW / "collected.json").write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")

    # Evaluate & Score jobs
    min_score = int(profile.get("minimum_score", 50))
    evaluated = [evaluate(job, min_score) for job in normalized]
    scored_jobs = [job for job in evaluated if not job.get("reject_reason")]

    report["after_hard_filter"] = len(scored_jobs)
    report["after_scoring"] = len(scored_jobs)

    # Deduplicate across sources
    unique = dedupe(scored_jobs)
    report["after_dedupe"] = len(unique)

    # Filter out previously sent jobs
    fresh = filter_unsent(unique, STATE)

    # Enrich with email / recruiter discovery & sort by score
    final_jobs = sorted(discover(fresh), key=lambda job: int(job.get("score", 0)), reverse=True)[:15]
    report["final_count"] = len(final_jobs)

    # Save reports
    run_report_text = json.dumps(report, indent=2, ensure_ascii=False)
    final_jobs_text = json.dumps(final_jobs, indent=2, ensure_ascii=False)

    (PROCESSED / "final_jobs.json").write_text(final_jobs_text, encoding="utf-8")
    (REPORTS / "run_report.json").write_text(run_report_text, encoding="utf-8")

    quality_md = generate_quality_report(normalized, unique, evaluated, final_jobs, report)

    logger.info(f"Pipeline executed successfully. Collected {len(normalized)} raw jobs -> {len(final_jobs)} qualified jobs.")
    print("\n" + quality_md)

    if args.dry_run:
        print("\n--- DRY RUN COMPLETE ---")
        print("Telegram delivery and state updates skipped.")
        print(f"Top {len(final_jobs)} Qualified Jobs:")
        for j in final_jobs:
            print(f"- [{j.get('score')}%] {j.get('title')} at {j.get('company')} ({j.get('location')}) -> {j.get('url')}")
        return 0

    if final_jobs:
        sent = send_digest(final_jobs, limit=10)
        mark_sent(sent, STATE)
        logger.info(f"Telegram delivered {len(sent)} jobs; state updated.")
    else:
        logger.info("No fresh eligible jobs; Telegram notification skipped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
