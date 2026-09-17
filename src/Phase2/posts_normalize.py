"""
posts_normalize.py

Converts data/recruiter_posts.csv (posts_scraper.py's output) into the same
job schema used everywhere else, so hiring posts can sit in the same merged
JSON as ATS jobs and LinkedIn job listings.

A hiring post isn't a "job" with a title/description in the usual sense --
it's a short text blob that mentions a role, a company, maybe an email and
an apply link. So this maps loosely:
    title       -> "Hiring post: <company or query>"
    description -> the post text itself (already truncated to 500 chars
                    by posts_scraper.py)
    url         -> apply_link if present, else the post_url
"""

import hashlib
import json
import os

import pandas as pd

INPUT_CSV = "data/recruiter_posts.csv"
OUTPUT_JSON = "data/linkedin_posts_normalized.json"


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"{INPUT_CSV} not found -- run posts_scraper.py first.")
        return

    df = pd.read_csv(INPUT_CSV)
    jobs = []

    for _, row in df.iterrows():
        company = str(row.get("company", "") or "").strip()
        query = str(row.get("query", "") or "").strip()
        url = str(row.get("apply_link", "") or "").strip() or str(row.get("post_url", "") or "").strip()

        if not url:
            continue  # nothing to point Akash to, skip

        job_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]

        jobs.append({
            "source": "linkedin_post",
            "company": company or "Unknown (see post)",
            "job_id": job_id,
            "title": f"Hiring post: {company or query}",
            "location": "",
            "description": str(row.get("description", "") or ""),
            "url": url,
            "posted_at": "",
            "recruiter_email": str(row.get("email", "") or "") or None,
        })

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Normalized {len(jobs)} hiring posts -> {OUTPUT_JSON}")


if __name__ == "__main__":
    main()