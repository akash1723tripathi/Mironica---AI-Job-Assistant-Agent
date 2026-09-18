"""
YC Work at a Startup Collector (Playwright-based).
Bypasses HTTP 406 anti-bot protections by utilizing Playwright browser automation.
Supports standalone `--test` execution mode.
"""

from __future__ import annotations
import sys
import time
import argparse
import logging
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

# Ensure repo root in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.processing.normalize import new_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("yc_collector")

STORAGE_STATE = Path("storage_state.json")

def collect(url: str = "https://www.workatastartup.com/jobs", max_scrolls: int = 5) -> list[dict]:
    jobs = []
    known_urls = set()
    logger.info(f"Starting YC collector for {url} using Playwright...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            if STORAGE_STATE.exists():
                context_kwargs["storage_state"] = str(STORAGE_STATE)

            context = browser.new_context(**context_kwargs)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # Scroll down to load more job listings
            for i in range(max_scrolls):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)

            # Fast in-browser JS evaluation to extract all job links & company info
            extracted_raw = page.evaluate("""
                () => {
                    const results = [];
                    const anchors = Array.from(document.querySelectorAll('a'));
                    let currentCompany = 'YC Startup';
                    
                    for (const a of anchors) {
                        const href = a.getAttribute('href') || '';
                        const text = a.innerText ? a.innerText.trim() : '';
                        
                        if (href.includes('/companies/')) {
                            if (text) {
                                currentCompany = text.split('\\n')[0].split('(')[0].trim();
                            }
                        } else if (/\\/jobs\\/\\d+/.test(href)) {
                            if (text && !['apply', 'learn more', 'view job'].includes(text.toLowerCase())) {
                                const container = a.closest('div, li, tr');
                                const contextText = container ? container.innerText.trim() : text;
                                results.push({
                                    href: href,
                                    title: text,
                                    company: currentCompany,
                                    context: contextText
                                });
                            }
                        }
                    }
                    return results;
                }
            """)

            for item in extracted_raw:
                href = item["href"]
                full_url = urljoin(url, href)
                if full_url in known_urls:
                    continue
                known_urls.add(full_url)

                jobs.append(new_job(
                    "yc",
                    source_id=full_url,
                    title=item["title"],
                    company=item["company"] or "YC Startup",
                    description=item["context"],
                    url=full_url,
                    apply_type="yc"
                ))

            browser.close()
    except Exception as e:
        logger.error(f"Error during YC collection: {e}")

    logger.info(f"YC collector finished. Collected {len(jobs)} jobs.")
    return jobs

def main():
    parser = argparse.ArgumentParser(description="YC Work at a Startup Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies = set()

    try:
        jobs = collect()
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
    except Exception as e:
        logger.error(f"YC test failed: {e}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "YC",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors
    }
    print(f"\n--- YC Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
