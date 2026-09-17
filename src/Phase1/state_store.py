"""
state_store.py

Tracks which jobs have already been shown, so tomorrow's 11 AM run doesn't
re-send a job that was already sent yesterday. This was completely missing
from the original pipeline -- every run treated every job as new.

Storage is a flat JSON file of seen job ids. Fine for the volumes this
project deals with (tens of jobs/day); move to SQLite later if it ever
needs to scale up.
"""

import hashlib
import json
import os

STATE_FILE = "data/seen_jobs.json"


def _job_key(job: dict) -> str:
    """Stable id for a job: source + company + job_id (or url as fallback)."""
    raw = f"{job.get('source','')}:{job.get('company','')}:{job.get('job_id') or job.get('url','')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_seen() -> set:
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()


def save_seen(seen: set):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, indent=2)


def filter_new(jobs: list) -> list:
    """Returns only jobs whose key hasn't been seen before, tagging each with its key."""
    seen = load_seen()
    new_jobs = []
    for job in jobs:
        key = _job_key(job)
        job["_key"] = key
        if key not in seen:
            new_jobs.append(job)
    return new_jobs


def mark_seen(jobs: list):
    """Call this after successfully sending a batch of jobs to Telegram."""
    seen = load_seen()
    for job in jobs:
        seen.add(job.get("_key") or _job_key(job))
    save_seen(seen)