"""
Authenticated LinkedIn content-search collector with diagnostics.
Supports standalone `--test` execution mode.
"""

from __future__ import annotations

import sys
import re
import time
import argparse
import logging
from pathlib import Path
from urllib.parse import quote

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.processing.normalize import new_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("linkedin_posts")

ROOT = Path(__file__).resolve().parents[2]
SEARCHES = (
    "hiring backend engineer", "hiring backend developer", "hiring software engineer",
    "hiring full stack engineer", "hiring golang engineer", "hiring go developer",
    "hiring node js engineer", "hiring backend intern", "hiring software engineer intern",
    "hiring full stack intern", "looking for backend engineer", "we are hiring backend",
    "engineering intern hiring", "associate software engineer hiring"
)
SELECTORS = (
    "div[componentkey^='update-card-focus']", "div[role='article']",
    "div[role='listitem']", "div.feed-shared-update-v2", "li.reusable-search__result-container"
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s)]+")
DM_ONLY = ("dm me", "dm if interested", "message me", "reach out via dm", "send me a dm")


def _url(card) -> str:
    for i in range(min(card.locator("a").count(), 30)):
        href = card.locator("a").nth(i).get_attribute("href") or ""
        if any(mark in href for mark in ("/feed/update/", "/posts/", "urn:li:activity")):
            return href.split("?")[0]
    return ""


def collect(max_per_query: int = 15, max_queries: int = 10) -> list[dict]:
    state = ROOT / "storage_state.json"
    if not state.exists():
        logger.warning("storage_state.json is missing; LinkedIn posts collector skipped")
        return []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright is unavailable; LinkedIn posts collector skipped")
        return []

    records, diagnostic = [], ROOT / "data" / "diagnostics"
    diagnostic.mkdir(parents=True, exist_ok=True)
    logger.info(f"Running LinkedIn Posts collector with max {max_queries} queries...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(state))
        page = context.new_page()

        for query in SEARCHES[:max_queries]:
            try:
                page.goto(f"https://www.linkedin.com/search/results/content/?keywords={quote(query)}", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1800)
                for _ in range(4):
                    page.mouse.wheel(0, 2200)
                    page.wait_for_timeout(700)

                selector = next((s for s in SELECTORS if page.locator(s).count()), "")
                if not selector:
                    safe = re.sub(r"[^a-z0-9]+", "_", query.lower())
                    page.screenshot(path=str(diagnostic / f"linkedin_posts_{safe}.png"), full_page=True)
                    (diagnostic / f"linkedin_posts_{safe}.html").write_text(page.content(), encoding="utf-8")
                    continue

                for i in range(min(page.locator(selector).count(), max_per_query)):
                    card = page.locator(selector).nth(i)
                    try:
                        text = " ".join(card.inner_text().split())
                        lower = text.lower()
                        if not any(x in lower for x in ("hiring", "looking for", "opening", "vacancy")) or any(x in lower for x in DM_ONLY):
                            continue

                        links = [x.rstrip(".,)") for x in URL.findall(text)]
                        apply = next((x for x in links if any(k in x.lower() for k in ("forms.gle", "google.com/forms", "careers", "jobs", "greenhouse", "lever", "ashby"))), "")
                        post_url = _url(card)
                        email = EMAIL.search(text)
                        job_link = ""

                        view = card.get_by_text("View job", exact=False)
                        if view.count():
                            job_link = view.first.get_attribute("href") or ""

                        if not (apply or job_link or email or post_url):
                            continue

                        recruiter = card.locator("span[dir='ltr']").first.inner_text().strip() if card.locator("span[dir='ltr']").count() else ""
                        
                        records.append(new_job(
                            "linkedin_posts",
                            source_id=post_url or apply or job_link,
                            recruiter_name=recruiter,
                            recruiter_email=email.group(0) if email else "",
                            email_source="linkedin_post" if email else "",
                            title=query.title(),
                            description=text[:1500],
                            url=apply or job_link or post_url,
                            apply_type="linkedin_post",
                            employment_type=""
                        ))
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Error querying '{query}': {e}")

        browser.close()

    logger.info(f"LinkedIn Posts collector finished. Collected {len(records)} posts.")
    return records


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Hiring Posts Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    try:
        posts = collect(max_per_query=15, max_queries=10)
        for p in posts:
            if p.get("company"):
                scanned_companies.add(p["company"])
    except Exception as e:
        logger.error(f"LinkedIn Posts test failed: {e}")
        posts = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "LinkedIn Hiring Posts",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(posts),
        "accepted": len(posts),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- LinkedIn Posts Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
