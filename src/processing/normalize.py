"""The canonical job contract shared by all collectors and consumers."""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

FIELDS = (
    "source", "source_id", "company", "title", "location", "description",
    "url", "posted_at", "employment_type", "experience", "recruiter_name",
    "recruiter_email", "email_source", "apply_type", "score", "reject_reason", "_key",
)


def clean_text(value: object) -> str:
    return " ".join(str(value or "").split())


def clean_url(value: object) -> str:
    url = clean_text(value)
    if not url:
        return ""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def new_job(source: str, **values: object) -> dict:
    """Create a complete canonical job record; unknown values stay empty."""
    job = {field: "" for field in FIELDS}
    job.update({"source": source, "score": 0})
    for key, value in values.items():
        if key in job:
            job[key] = clean_text(value) if key not in {"score"} else value
    job["url"] = clean_url(job["url"])
    return job


def normalize(job: dict) -> dict:
    """Defensively normalize a collector record to the canonical contract."""
    values = dict(job)
    source = str(values.pop("source", "unknown"))
    result = new_job(source, **values)
    result["source_id"] = clean_text(result["source_id"])
    if not result["source_id"]:
        result["source_id"] = result["url"]
    return result


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
