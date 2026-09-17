"""
linkedin_enrich.py

Fetches the REAL job description for each row in data/jobs.csv (produced by
jobs_scraper.py), using an authenticated Playwright session -- not plain
`requests` like the old enrich_jobs.py did.

This is the actual fix for the original bug: the old script's `requests.get()`
had no cookies, so LinkedIn served it a login wall and the description came
back empty every time. Here we reuse storage_state.json (the same session
login.py already saves), so the page renders as if you're logged in and the
description box is actually present in the HTML this time.

Account-safety notes (read before running daily):
  - headless=True by default -- lower footprint than a visible browser
  - random delay between requests, and a hard cap per run (MAX_JOBS below)
  - already-enriched URLs are skipped on rerun, so retrying a failed run
    doesn't re-hit jobs you already have
  - if descriptions keep coming back empty, your storage_state.json has
    probably expired -- re-run login.py to refresh it
"""

import json
import os
import random
import time

import pandas as pd
from playwright.sync_api import sync_playwright

INPUT_CSV = "data/jobs.csv"
OUTPUT_JSON = "data/linkedin_jobs_enriched.json"
STATE_FILE = "storage_state.json"
MAX_JOBS = 60  # cap per run -- keep LinkedIn traffic low


def load_existing() -> dict:
    """Keyed by apply_link, so reruns don't refetch what already worked."""
    if not os.path.exists(OUTPUT_JSON):
        return {}
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        try:
            jobs = json.load(f)
            return {j["url"]: j for j in jobs if j.get("url")}
        except json.JSONDecodeError:
            return {}


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"{INPUT_CSV} not found -- run jobs_scraper.py first.")
        return

    df = pd.read_csv(INPUT_CSV)
    existing = load_existing()

    todo = [
        row for _, row in df.iterrows()
        if row.get("apply_link") and row["apply_link"] not in existing
    ][:MAX_JOBS]

    print(f"{len(existing)} already enriched, {len(todo)} to fetch this run (cap {MAX_JOBS})")

    if not todo:
        print("Nothing new to enrich.")
        return

    if not os.path.exists(STATE_FILE):
        print(f"{STATE_FILE} not found -- run login.py first to create a session.")
        return

    results = list(existing.values())
    empty_streak = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        for i, row in enumerate(todo):
            url = row["apply_link"]
            print(f"[{i+1}/{len(todo)}] {row.get('role','')} @ {row.get('company','')}")

            desc = ""
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                box = page.locator(".show-more-less-html__markup").first
                if box.count() > 0:
                    desc = box.inner_text().strip()
            except Exception as e:
                print(f"  error: {e}")

            if not desc:
                empty_streak += 1
                print("  (empty description)")
            else:
                empty_streak = 0

            if empty_streak >= 5:
                print("\n5 empty descriptions in a row -- storage_state.json is probably "
                      "expired. Stopping early. Re-run login.py, then run this again.")
                break

            results.append({
                "source": "linkedin",
                "company": row.get("company", ""),
                "job_id": str(abs(hash(url)))[:12],
                "title": row.get("role", ""),
                "location": row.get("location", ""),
                "description": desc,
                "url": url,
                "posted_at": row.get("posted", ""),
            })

            time.sleep(random.uniform(2, 5))

        browser.close()

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} total enriched jobs -> {OUTPUT_JSON}")


if __name__ == "__main__":
    main()