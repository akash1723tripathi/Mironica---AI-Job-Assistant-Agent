"""
Cross-source deduplication using stable URLs, normalized job identities,
and strict source priority ordering.
"""

from __future__ import annotations

import hashlib
import re
from .normalize import clean_url

SOURCE_PRIORITY = {
    "linkedin_jobs": 100,
    "greenhouse": 90,
    "lever": 85,
    "ashby": 80,
    "workday": 75,
    "zoho_recruit": 70,
    "yc": 65,
    "career_pages": 60,
    "linkedin_posts": 50,
}


def get_source_priority(source: str) -> int:
    return SOURCE_PRIORITY.get(str(source or "").lower(), 10)


def _token(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def job_key(job: dict) -> str:
    source = _token(job.get("source"))
    source_id = str(job.get("source_id") or "").strip()
    if source_id.startswith(("http://", "https://")):
        source_id = clean_url(source_id)
    if source and source_id:
        raw = f"source:{source}:{source_id.lower()}"
    else:
        raw = "fallback:" + ":".join((_token(job.get("company")), _token(job.get("title")), _token(job.get("location"))))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def duplicate_evidence(job: dict) -> tuple[str, str]:
    """Normalize company and title for semantic deduplication across sources."""
    company = _token(job.get("company"))
    title = _token(job.get("title"))
    return (company, title)


def dedupe(jobs: list[dict]) -> list[dict]:
    """
    Deduplicate jobs by canonical key, URL, and company+title hash.
    Higher priority sources take precedence over lower priority sources.
    """
    # Sort by source priority descending, then score descending
    sorted_jobs = sorted(
        jobs,
        key=lambda j: (get_source_priority(j.get("source")), j.get("score", 0)),
        reverse=True
    )

    seen_keys, seen_urls, seen_evidence = set(), set(), set()
    unique = []

    for job in sorted_jobs:
        key = job_key(job)
        url = clean_url(job.get("url"))
        company, title = duplicate_evidence(job)

        if key in seen_keys:
            continue
        if url and url in seen_urls:
            continue
        if company and title and (company, title) in seen_evidence:
            continue

        job["_key"] = key
        seen_keys.add(key)
        if url:
            seen_urls.add(url)
        if company and title:
            seen_evidence.add((company, title))
            
        unique.append(job)

    return unique
