"""
ats_scanner.py

Fetches job postings directly from ATS public APIs — Greenhouse, Lever, Ashby.
No login, no HTML scraping, no fragile CSS selectors. The full job description
comes back in the same response, so there is no separate "enrichment" step
that can silently fail like the old requests+BeautifulSoup approach did.

How to find a company's board token:
  Greenhouse -> careers page URL looks like boards.greenhouse.io/<token>
                or the page footer says "Powered by Greenhouse" with that URL
  Lever      -> careers page URL looks like jobs.lever.co/<token>
  Ashby      -> careers page URL looks like jobs.ashbyhq.com/<token>

Add tokens to config/ats_companies.json. Wrong/expired tokens just return a
404 and get skipped — they don't break the run.
"""

import json
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-scanner/1.0)"}
TIMEOUT = 20


def fetch_greenhouse(token: str):
    """Greenhouse public board API. Returns list of normalized job dicts."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    jobs = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  [greenhouse:{token}] skipped ({r.status_code})")
            return jobs
        data = r.json()
        for j in data.get("jobs", []):
            jobs.append({
                "source": "greenhouse",
                "company": token,
                "job_id": str(j.get("id", "")),
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "description": j.get("content", "") or "",
                "url": j.get("absolute_url", ""),
                "posted_at": j.get("updated_at", ""),
            })
    except Exception as e:
        print(f"  [greenhouse:{token}] error: {e}")
    return jobs


def fetch_lever(token: str):
    """Lever public postings API. Returns list of normalized job dicts."""
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    jobs = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  [lever:{token}] skipped ({r.status_code})")
            return jobs
        data = r.json()
        for j in data:
            desc = j.get("descriptionPlain") or j.get("description", "") or ""
            lists = j.get("lists", []) or []
            extra = " ".join(
                (item.get("text", "") + " " + " ".join(item.get("content", []) if isinstance(item.get("content"), list) else [str(item.get("content", ""))]))
                for item in lists
            )
            jobs.append({
                "source": "lever",
                "company": token,
                "job_id": j.get("id", ""),
                "title": j.get("text", ""),
                "location": (j.get("categories") or {}).get("location", ""),
                "description": (desc + " " + extra).strip(),
                "url": j.get("hostedUrl", ""),
                "posted_at": j.get("createdAt", ""),
            })
    except Exception as e:
        print(f"  [lever:{token}] error: {e}")
    return jobs


def fetch_ashby(token: str):
    """Ashby public job-board API. Returns list of normalized job dicts."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false"
    jobs = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  [ashby:{token}] skipped ({r.status_code})")
            return jobs
        data = r.json()
        for j in data.get("jobs", []):
            if j.get("isListed") is False:
                continue
            jobs.append({
                "source": "ashby",
                "company": token,
                "job_id": j.get("id", ""),
                "title": j.get("title", ""),
                "location": j.get("location", ""),
                "description": j.get("descriptionPlain", "") or "",
                "url": j.get("jobUrl", "") or j.get("applyUrl", ""),
                "posted_at": j.get("publishedAt", ""),
            })
    except Exception as e:
        print(f"  [ashby:{token}] error: {e}")
    return jobs


def scan_all(config_path: str = "config/ats_companies.json"):
    """Reads config/ats_companies.json and scans every configured company."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    all_jobs = []

    for token in config.get("greenhouse", []):
        print(f"Scanning greenhouse -> {token}")
        all_jobs.extend(fetch_greenhouse(token))
        time.sleep(0.5)

    for token in config.get("lever", []):
        print(f"Scanning lever -> {token}")
        all_jobs.extend(fetch_lever(token))
        time.sleep(0.5)

    for token in config.get("ashby", []):
        print(f"Scanning ashby -> {token}")
        all_jobs.extend(fetch_ashby(token))
        time.sleep(0.5)

    print(f"\nTotal jobs fetched: {len(all_jobs)}")
    return all_jobs


if __name__ == "__main__":
    jobs = scan_all()
    with open("data/ats_jobs_raw.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print("Saved -> data/ats_jobs_raw.json")