"""
Configurable public static career-page collector.
Supports standalone `--test` execution mode.
"""

from __future__ import annotations

import sys
import time
import argparse
import logging
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.processing.normalize import new_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("career_pages")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def collect(pages: list[dict], source: str = "career_pages") -> tuple[list[dict], list[str]]:
    records, failures = [], []
    logger.info(f"Starting {source} collector for {len(pages)} pages...")

    for item in pages:
        if not item.get("enabled", True) or not item.get("career_url"):
            continue
        try:
            url = item["career_url"]
            response = requests.get(url, timeout=15, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            selectors = item.get("job_selectors", ["a[href*='job']", "a[href*='career']"])
            for selector in selectors:
                links.extend(soup.select(selector))
            
            seen_urls = set()
            for anchor in links:
                title = anchor.get_text(" ", strip=True)
                href = urljoin(url, anchor.get("href", ""))
                if title and href and href not in seen_urls:
                    seen_urls.add(href)
                    records.append(new_job(
                        source,
                        source_id=href,
                        company=item.get("company", ""),
                        title=title,
                        location=item.get("country", ""),
                        url=href,
                        apply_type="career_page"
                    ))
        except Exception as exc:
            failures.append(f"{item.get('company', '?')}: {exc}")

    logger.info(f"{source} collector finished. Collected {len(records)} jobs, {len(failures)} failures.")
    return records, failures


def main():
    parser = argparse.ArgumentParser(description="Career Pages Jobs Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    sample_pages = [
        {"company": "Sample Company", "career_url": "https://news.ycombinator.com/jobs", "job_selectors": ["a[href*='item']"], "enabled": True}
    ]

    try:
        jobs, failures = collect(sample_pages)
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
        errors = len(failures)
    except Exception as e:
        logger.error(f"Career pages test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "Career Pages",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- Career Pages Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
