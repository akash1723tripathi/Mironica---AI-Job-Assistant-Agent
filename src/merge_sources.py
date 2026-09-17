"""
merge_sources.py

Combines all three sources into one list, dedupes against past runs, scores
eligibility, and writes the result to data/final_review.json.

Deliberately does NOT touch Telegram. Run this, open final_review.json,
check the jobs in it actually look right -- once that's satisfying, swap
the last line of this file for a send_digest() call (or just point
run_scan.py's send_digest at this merged list instead of ats-only).

Run order for a full local pass:
    python src/phase1/ats_scanner.py          # writes data/ats_jobs_raw.json
    python src/phase2/jobs_scraper.py          # writes data/jobs.csv
    python src/phase2/linkedin_enrich.py       # writes data/linkedin_jobs_enriched.json
    python src/phase2/posts_scraper.py         # writes data/recruiter_posts.csv (needs storage_state.json)
    python src/phase2/posts_normalize.py       # writes data/linkedin_posts_normalized.json
    python src/merge_sources.py                # writes data/final_review.json
"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "phase1"))

from state_store import filter_new  # noqa: E402
from eligibility import filter_eligible  # noqa: E402

SOURCES = [
    "data/ats_jobs_raw.json",
    "data/linkedin_jobs_enriched.json",
    "data/linkedin_posts_normalized.json",
]

OUTPUT = "data/final_review.json"


def load_json(path):
    if not os.path.exists(path):
        print(f"  (skipping {path} -- not found yet)")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    all_jobs = []
    for path in SOURCES:
        jobs = load_json(path)
        print(f"{path}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

    print(f"\nTotal combined: {len(all_jobs)}")

    new_jobs = filter_new(all_jobs)
    print(f"New (not seen before): {len(new_jobs)}")

    eligible = filter_eligible(new_jobs)
    print(f"Eligible (score >= 70): {len(eligible)}")

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(eligible, f, indent=2, ensure_ascii=False)

    print(f"\nSaved -> {OUTPUT}")
    print("Review this file. Not marked as 'seen' yet -- state_store only")
    print("updates once you actually send a digest (mark_seen), so re-running")
    print("this script is safe and repeatable while you're still checking quality.")


if __name__ == "__main__":
    main()