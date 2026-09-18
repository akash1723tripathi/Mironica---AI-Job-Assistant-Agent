"""
Low-volume LinkedIn guest job search collector plus optional authenticated enrichment.
Supports standalone `--test` execution mode.
"""

from __future__ import annotations

import sys
import json
import time
import argparse
import logging
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.processing.normalize import new_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("linkedin_jobs")

ROOT = Path(__file__).resolve().parents[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"}


def collect(search_config: dict, max_per_query: int = 25, max_queries: int = 18) -> list[dict]:
    jobs, errors = [], []
    locations = search_config.get("locations", ["India", "Noida", "Bengaluru", "Gurugram", "Remote"])
    roles = search_config.get("roles", ["Software Engineer", "Backend Engineer", "Full Stack Engineer", "Associate Software Engineer"])
    
    queries = [(location, role) for location in locations for role in roles]
    logger.info(f"Running LinkedIn Jobs collector with max {max_queries} queries...")

    for location, role in queries[:max_queries]:
        url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search" + f"?keywords={quote(role)}&location={quote(location)}&f_TPR=r86400&start=0"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                errors.append(f"{role} / {location}: HTTP {response.status_code}")
                continue

            cards = BeautifulSoup(response.text, "html.parser").find_all("li")[:max_per_query]
            for card in cards:
                title = card.find("h3")
                if not title:
                    continue
                link = card.find("a", class_="base-card__full-link")
                company = card.find("h4")
                place = card.find("span", class_="job-search-card__location")
                date = card.find("time")
                href = link.get("href", "") if link else ""
                
                jobs.append(new_job(
                    "linkedin_jobs",
                    source_id=href,
                    company=company.get_text(strip=True) if company else "",
                    title=title.get_text(strip=True),
                    location=place.get_text(strip=True) if place else "",
                    url=href,
                    posted_at=date.get("datetime", "") if date else "",
                    apply_type="linkedin"
                ))
            time.sleep(0.4)
        except Exception as exc:
            errors.append(f"{role} / {location}: {exc}")

    logger.info(f"LinkedIn Jobs collector finished. Collected {len(jobs)} jobs.")
    return jobs


def enrich(jobs: list[dict], limit: int) -> tuple[list[dict], str]:
    """Use the saved LinkedIn session when Playwright/browser state is available."""
    state = ROOT / "storage_state.json"
    if not jobs:
        return jobs, ""
    if not state.exists():
        return jobs, "storage_state.json unavailable; discovery records retained without descriptions"
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return jobs, "playwright unavailable; discovery records retained without descriptions"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(state))
            page = context.new_page()
            for job in jobs[:limit]:
                try:
                    page.goto(job["url"], wait_until="domcontentloaded", timeout=20000)
                    page.wait_for_timeout(800)
                    box = page.locator(".show-more-less-html__markup").first
                    if box.count():
                        job["description"] = box.inner_text().strip()
                except Exception:
                    continue
            browser.close()
        return jobs, ""
    except Exception as exc:
        return jobs, f"LinkedIn enrichment unavailable: {exc}"


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Jobs Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    search_file = ROOT / "config" / "search.json"
    if search_file.exists():
        with open(search_file, "r", encoding="utf-8") as f:
            search_cfg = json.load(f)
    else:
        search_cfg = {
            "locations": ["India", "Noida", "Bengaluru", "Gurugram"],
            "roles": ["Backend Engineer", "Software Engineer", "Associate Software Engineer", "SDE"]
        }

    try:
        jobs = collect(search_cfg, max_per_query=25, max_queries=18)
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
    except Exception as e:
        logger.error(f"LinkedIn Jobs test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "LinkedIn Jobs",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- LinkedIn Jobs Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
