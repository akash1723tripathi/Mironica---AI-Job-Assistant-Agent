"""
Public Greenhouse, Lever, and Ashby board collectors.
Supports multi-threaded parallel fetching and standalone `--test` execution mode.
"""

from __future__ import annotations

import sys
import json
import time
import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.processing.normalize import new_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ats_collector")

ROOT = Path(__file__).resolve().parents[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def _get(url: str) -> object:
    response = requests.get(url, headers=HEADERS, timeout=12)
    response.raise_for_status()
    return response.json()


def _greenhouse(board: dict) -> list[dict]:
    data = _get(f"https://boards-api.greenhouse.io/v1/boards/{board['token']}/jobs?content=true")
    jobs = data.get("jobs", [])
    return [
        new_job(
            "greenhouse",
            source_id=j.get("id", ""),
            company=board["company"],
            title=j.get("title", ""),
            location=(j.get("location") or {}).get("name", ""),
            description=j.get("content", ""),
            url=j.get("absolute_url", ""),
            posted_at=j.get("updated_at", ""),
            apply_type="greenhouse"
        )
        for j in jobs
    ]


def _lever(board: dict) -> list[dict]:
    data = _get(f"https://api.lever.co/v0/postings/{board['token']}?mode=json")
    jobs = []
    if isinstance(data, list):
        for j in data:
            extra = " ".join(str(item.get("text", "")) + " " + str(item.get("content", "")) for item in j.get("lists", []) or [])
            jobs.append(new_job(
                "lever",
                source_id=j.get("id", ""),
                company=board["company"],
                title=j.get("text", ""),
                location=(j.get("categories") or {}).get("location", ""),
                description=(j.get("descriptionPlain") or j.get("description", "")) + " " + extra,
                url=j.get("hostedUrl", ""),
                posted_at=j.get("createdAt", ""),
                employment_type=(j.get("categories") or {}).get("commitment", ""),
                apply_type="lever"
            ))
    return jobs


def _ashby(board: dict) -> list[dict]:
    data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{board['token']}?includeCompensation=false")
    jobs = data.get("jobs", [])
    return [
        new_job(
            "ashby",
            source_id=j.get("id", ""),
            company=board["company"],
            title=j.get("title", ""),
            location=j.get("location", ""),
            description=j.get("descriptionPlain", ""),
            url=j.get("jobUrl", "") or j.get("applyUrl", ""),
            posted_at=j.get("publishedAt", ""),
            employment_type=j.get("employmentType", ""),
            apply_type="ashby"
        )
        for j in jobs
        if j.get("isListed") is not False
    ]


def fetch_single_board(board: dict) -> tuple[list[dict], str | None]:
    platform = board.get("platform", "").lower()
    fetchers = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}
    if platform not in fetchers:
        return [], None
    try:
        results = fetchers[platform](board)
        return results, None
    except Exception as exc:
        return [], f"{board.get('company', board.get('token', '?'))} ({platform}): {exc}"


def collect(boards: list[dict], platform: str = None) -> tuple[list[dict], list[str]]:
    active_boards = [
        b for b in boards
        if (platform is None or b.get("platform") == platform) and b.get("enabled", True)
    ]
    logger.info(f"Starting ATS collector for {len(active_boards)} active boards...")

    records, failures = [], []

    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_board = {executor.submit(fetch_single_board, b): b for b in active_boards}
        for future in as_completed(future_to_board):
            res, err = future.result()
            if res:
                records.extend(res)
            if err:
                failures.append(err)

    logger.info(f"ATS collector finished. Collected {len(records)} jobs, {len(failures)} failures.")
    return records, failures


def main():
    parser = argparse.ArgumentParser(description="ATS Jobs Collector (Greenhouse, Lever, Ashby)")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    parser.add_argument("--platform", choices=["greenhouse", "lever", "ashby"], help="Filter by platform")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    # Load merged sources if available
    sources_gen = ROOT / "config" / "sources.generated.json"
    sources_seed = ROOT / "config" / "sources.seed.json"

    boards = []
    if sources_gen.exists():
        with open(sources_gen, "r", encoding="utf-8") as f:
            boards.extend(json.load(f).get("ats_boards", []))
    if sources_seed.exists():
        with open(sources_seed, "r", encoding="utf-8") as f:
            boards.extend(json.load(f).get("ats_boards", []))

    # Deduplicate by company + platform
    seen_keys = set()
    dedup_boards = []
    for b in boards:
        key = (b.get("company"), b.get("platform"))
        if key not in seen_keys:
            seen_keys.add(key)
            dedup_boards.append(b)

    try:
        jobs, failures = collect(dedup_boards, platform=args.platform)
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
        errors = len(failures)
    except Exception as e:
        logger.error(f"ATS test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": f"ATS ({args.platform or 'All'})",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- ATS Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
