"""The canonical job contract shared by all collectors and consumers."""

from __future__ import annotations

import html as _html
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

FIELDS = (
    "source", "source_id", "company", "title", "location", "description",
    "url", "post_url", "posted_at", "employment_type", "experience", "recruiter_name",
    "recruiter_email", "email_source", "apply_type", "contact_type", "score",
    "reject_reason", "_key",
)

# Greenhouse/Lever/Ashby descriptions (and Telegram-rendered output) often carry raw HTML
# markup and escaped entities (e.g. "&lt;div class=&quot;...&quot;&gt;"). This strips both
# so scoring, dedupe and Telegram messages all see plain, readable text.
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(raw: str) -> str:
    if not raw:
        return ""
    # Unescape entities first in case the HTML itself arrived already-escaped
    # (e.g. "&lt;div&gt;" rather than literal "<div>").
    unescaped = _html.unescape(raw)
    if "<" in unescaped and ">" in unescaped:
        text = BeautifulSoup(unescaped, "html.parser").get_text(" ")
    else:
        text = unescaped
    # In case any stray tags survive bs4 (malformed markup), strip them too.
    text = _TAG_RE.sub(" ", text)
    return _html.unescape(text)


def clean_text(value: object) -> str:
    return " ".join(str(value or "").split())


def clean_description(value: object) -> str:
    """Like clean_text, but also strips HTML tags/entities. Use for any field that may
    contain raw markup from an ATS API (title/description primarily)."""
    return " ".join(_strip_html(str(value or "")).split())


def clean_url(value: object) -> str:
    url = clean_text(value)
    if not url:
        return ""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


# Fields that can arrive carrying raw HTML (mainly ATS API payloads) get HTML-stripped;
# everything else just gets whitespace-collapsed.
_HTML_FIELDS = {"title", "description"}


def new_job(source: str, **values: object) -> dict:
    """Create a complete canonical job record; unknown values stay empty."""
    job = {field: "" for field in FIELDS}
    job.update({"source": source, "score": 0})
    for key, value in values.items():
        if key not in job:
            continue
        if key == "score":
            job[key] = value
        elif key in _HTML_FIELDS:
            job[key] = clean_description(value)
        else:
            job[key] = clean_text(value)
    job["url"] = clean_url(job["url"])
    job["post_url"] = clean_url(job["post_url"])
    return job


def classify_contact(job: dict) -> str:
    """Decide how Akash can act on this job, independent of which site it came from:
    - "form": a real apply/form/careers link is known (ATS boards always qualify here,
      since their url IS the application page; a LinkedIn post qualifies if it links a
      form/careers/job page).
    - "email_only": no apply link, but a recruiter email is known — a cold email is the
      next step.
    - "post_only": neither an apply link nor an email — only the original post is known,
      Akash opens it himself to judge next steps.
    """
    if job.get("url"):
        return "form"
    if job.get("recruiter_email"):
        return "email_only"
    if job.get("post_url"):
        return "post_only"
    return ""


def normalize(job: dict) -> dict:
    """Defensively normalize a collector record to the canonical contract."""
    values = dict(job)
    source = str(values.pop("source", "unknown"))
    result = new_job(source, **values)
    result["source_id"] = clean_text(result["source_id"])
    if not result["source_id"]:
        result["source_id"] = result["url"] or result["post_url"]
    result["contact_type"] = classify_contact(result)
    return result


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
