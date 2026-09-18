"""
Configurable collector for public Zoho Recruit career pages.
Supports standalone `--test` execution mode.
"""

from __future__ import annotations

import sys
import time
import argparse
import logging
from pathlib import Path

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.collectors.career_pages import collect as collect_pages

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("zoho_recruit")


def collect(sites: list[dict]):
    pages = [
        {
            **site,
            "career_url": site.get("career_url", ""),
            "job_selectors": site.get("job_selectors", ["a[href*='job']", ".job-title a"])
        }
        for site in sites
        if site.get("career_url")
    ]
    return collect_pages(pages, "zoho_recruit")


def main():
    parser = argparse.ArgumentParser(description="Zoho Recruit Jobs Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    sample_sites = []
    try:
        jobs, failures = collect(sample_sites)
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
        errors = len(failures)
    except Exception as e:
        logger.error(f"Zoho Recruit test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "Zoho Recruit",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- Zoho Recruit Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
