"""
Workday Public Search API Collector.
Queries Workday `wday/cxs` REST endpoints per company.
Supports standalone `--test` execution mode.
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
logger = logging.getLogger("workday_collector")

ROOT = Path(__file__).resolve().parents[2]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def fetch_workday_company(site: dict, limit: int = 20) -> list[dict]:
    domain = site.get("domain")
    token = site.get("token")
    site_name = site.get("site", "External")
    company = site.get("company", token)

    if not domain or not token:
        return []

    url = f"https://{domain}/wday/cxs/{token}/{site_name}/jobs"
    payload = {"appliedFacets": {}, "limit": limit, "offset": 0, "searchText": ""}
    
    jobs = []
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=12)
        if resp.status_code != 200:
            logger.warning(f"Workday {company} returned HTTP {resp.status_code}")
            return []

        data = resp.json()
        postings = data.get("jobPostings", [])
        
        for p in postings:
            title = p.get("title", "")
            ext_path = p.get("externalPath", "")
            full_url = f"https://{domain}{ext_path}" if ext_path else f"https://{domain}"
            location = p.get("locationsText", "")
            posted = p.get("postedOn", "")

            jobs.append(new_job(
                "workday",
                source_id=full_url,
                company=company,
                title=title,
                location=location,
                description=f"{title} at {company}. Location: {location}. Posted: {posted}",
                url=full_url,
                posted_at=posted,
                apply_type="workday"
            ))
    except Exception as exc:
        logger.error(f"Error fetching Workday for {company}: {exc}")

    return jobs


def collect(sites: list[dict], limit_per_site: int = 20) -> list[dict]:
    logger.info(f"Starting Workday collector for {len(sites)} sites...")
    records = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_site = {executor.submit(fetch_workday_company, site, limit_per_site): site for site in sites}
        for future in as_completed(future_to_site):
            res = future.result()
            if res:
                records.extend(res)

    logger.info(f"Workday collector finished. Collected {len(records)} jobs.")
    return records


def main():
    parser = argparse.ArgumentParser(description="Workday Jobs Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    sources_gen = ROOT / "config" / "sources.generated.json"
    sources_seed = ROOT / "config" / "sources.seed.json"

    sites = []
    if sources_gen.exists():
        with open(sources_gen, "r", encoding="utf-8") as f:
            sites.extend(json.load(f).get("workday", []))
    if sources_seed.exists():
        with open(sources_seed, "r", encoding="utf-8") as f:
            sites.extend(json.load(f).get("workday", []))

    if not sites:
        sites = [
            {"company": "Adobe", "token": "adobe", "domain": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced"},
            {"company": "Nvidia", "token": "nvidia", "domain": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite"},
            {"company": "Salesforce", "token": "salesforce", "domain": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site"}
        ]

    try:
        jobs = collect(sites)
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
    except Exception as e:
        logger.error(f"Workday test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "Workday",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- Workday Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
