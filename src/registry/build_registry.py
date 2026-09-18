"""
Registry Builder for ATS boards.
Supports two modes:
1. `python src/registry/build_registry.py`: Scans seed list, validates active boards, populates config/sources.generated.json
2. `python src/registry/build_registry.py --verify`: Validates all ATS entries and generates data/reports/registry_report.json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.registry.seed_companies import SEED_COMPANIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_registry")

GENERATED_SOURCES_PATH = Path("config/sources.generated.json")
SEED_SOURCES_PATH = Path("config/sources.seed.json")
REGISTRY_REPORT_PATH = Path("data/reports/registry_report.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def validate_greenhouse(token: str) -> tuple[bool, str, int]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            return True, f"Found {len(jobs)} jobs", len(jobs)
        return False, f"HTTP {resp.status_code}", 0
    except Exception as e:
        return False, str(e), 0

def validate_lever(token: str) -> tuple[bool, str, int]:
    url = f"https://api.lever.co/v0/postings/{token}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return True, f"Found {len(data)} postings", len(data)
            return True, "Valid board", 0
        return False, f"HTTP {resp.status_code}", 0
    except Exception as e:
        return False, str(e), 0

def validate_ashby(token: str) -> tuple[bool, str, int]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            return True, f"Found {len(jobs)} jobs", len(jobs)
        return False, f"HTTP {resp.status_code}", 0
    except Exception as e:
        return False, str(e), 0

def validate_workday(domain: str, token: str, site: str) -> tuple[bool, str, int]:
    if not domain or not site:
        return False, "Missing domain/site configuration", 0
    url = f"https://{domain}/wday/cxs/{token}/{site}/jobs"
    payload = {"appliedFacets": {}, "limit": 5, "offset": 0, "searchText": ""}
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("total", 0)
            return True, f"Found {total} jobs", total
        return False, f"HTTP {resp.status_code}", 0
    except Exception as e:
        return False, str(e), 0

def validate_entry(entry: dict) -> dict:
    platform = entry.get("platform", "").lower()
    company = entry.get("company", "Unknown")
    token = entry.get("token", "")

    valid = False
    reason = "Unsupported platform"
    job_count = 0

    if platform == "greenhouse":
        valid, reason, job_count = validate_greenhouse(token)
    elif platform == "lever":
        valid, reason, job_count = validate_lever(token)
    elif platform == "ashby":
        valid, reason, job_count = validate_ashby(token)
    elif platform == "workday":
        domain = entry.get("domain", "")
        site = entry.get("site", "")
        valid, reason, job_count = validate_workday(domain, token, site)
    
    result = dict(entry)
    result["valid"] = valid
    result["reason"] = reason
    result["job_count"] = job_count
    return result

def build_registry():
    logger.info(f"Scanning {len(SEED_COMPANIES)} seed companies for active ATS boards...")
    validated_boards = []
    failed_boards = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_entry = {executor.submit(validate_entry, item): item for item in SEED_COMPANIES}
        for future in as_completed(future_to_entry):
            res = future.result()
            if res["valid"]:
                logger.info(f"[VALID] {res['platform'].upper()} - {res['company']} ({res['reason']})")
                board_item = {
                    "platform": res["platform"],
                    "company": res["company"],
                    "token": res["token"],
                    "country": res.get("country", "Global"),
                    "category": res.get("category", "tech"),
                    "enabled": True
                }
                if res["platform"] == "workday":
                    board_item["domain"] = res.get("domain")
                    board_item["site"] = res.get("site")
                validated_boards.append(board_item)
            else:
                logger.warning(f"[INVALID] {res['platform'].upper()} - {res['company']}: {res['reason']}")
                failed_boards.append(res)

    generated_data = {
        "ats_boards": [b for b in validated_boards if b["platform"] in ["greenhouse", "lever", "ashby"]],
        "workday": [b for b in validated_boards if b["platform"] == "workday"],
        "zoho_recruit": [],
        "career_pages": []
    }

    GENERATED_SOURCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GENERATED_SOURCES_PATH, "w", encoding="utf-8") as f:
        json.dump(generated_data, f, indent=2)

    logger.info(f"Registry built: {len(validated_boards)} valid boards saved to {GENERATED_SOURCES_PATH}")
    return validated_boards, failed_boards

def verify_registry():
    logger.info("Running registry verification mode (--verify)...")
    
    # Load seed and generated registries
    seed_entries = []
    if SEED_SOURCES_PATH.exists():
        with open(SEED_SOURCES_PATH, "r", encoding="utf-8") as f:
            s_data = json.load(f)
            seed_entries.extend(s_data.get("ats_boards", []))
            seed_entries.extend(s_data.get("workday", []))

    # Also include SEED_COMPANIES catalog
    all_to_scan = list(SEED_COMPANIES)

    # Load existing generated if available
    existing_generated = []
    if GENERATED_SOURCES_PATH.exists():
        with open(GENERATED_SOURCES_PATH, "r", encoding="utf-8") as f:
            g_data = json.load(f)
            existing_generated.extend(g_data.get("ats_boards", []))
            existing_generated.extend(g_data.get("workday", []))

    # Deduplicate scan list by company + platform
    seen_keys = set()
    scan_list = []
    for item in all_to_scan + seed_entries + existing_generated:
        key = (item.get("company"), item.get("platform"))
        if key not in seen_keys:
            seen_keys.add(key)
            scan_list.append(item)

    logger.info(f"Verifying total {len(scan_list)} ATS entries...")
    valid_count = 0
    dead_count = 0
    failures = []
    provider_counts = {"greenhouse": 0, "lever": 0, "ashby": 0, "workday": 0, "zoho": 0}

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_entry = {executor.submit(validate_entry, item): item for item in scan_list}
        for future in as_completed(future_to_entry):
            res = future.result()
            platform = res.get("platform", "").lower()
            if res["valid"]:
                valid_count += 1
                provider_counts[platform] = provider_counts.get(platform, 0) + 1
            else:
                dead_count += 1
                failures.append({
                    "company": res.get("company"),
                    "platform": platform,
                    "token": res.get("token"),
                    "reason": res.get("reason")
                })

    report = {
        "companies_scanned": len(scan_list),
        "valid_boards": valid_count,
        "dead_boards": dead_count,
        "newly_added_companies": len(scan_list) - len(existing_generated),
        "removed_companies": dead_count,
        "provider_wise_counts": provider_counts,
        "validation_failures": failures
    }

    REGISTRY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Verification complete. Valid: {valid_count}, Dead: {dead_count}. Report saved to {REGISTRY_REPORT_PATH}")
    return report

def main():
    parser = argparse.ArgumentParser(description="Registry Builder & Verifier")
    parser.add_argument("--verify", action="store_true", help="Run in verification mode and generate registry_report.json")
    args = parser.parse_args()

    if args.verify:
        report = verify_registry()
        print(json.dumps(report, indent=2))
        if report["valid_boards"] < 100:
            print(f"[!] WARNING: Valid boards count ({report['valid_boards']}) is below 100 criteria.")
            sys.exit(1)
    else:
        valid_boards, failed = build_registry()
        print(f"[+] Registry build finished with {len(valid_boards)} valid boards.")

if __name__ == "__main__":
    main()
