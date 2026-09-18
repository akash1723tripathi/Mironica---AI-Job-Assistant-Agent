"""Persistent sent-job state. Only confirmed Telegram deliveries are stored."""

from __future__ import annotations

import json
from pathlib import Path

from .dedupe import job_key
from .normalize import utc_now


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def filter_unsent(jobs: list[dict], path: Path) -> list[dict]:
    sent = load(path)
    result = []
    for job in jobs:
        key = job.get("_key") or job_key(job)
        job["_key"] = key
        # URL comparison supports state written before URL query normalization.
        legacy_match = any(
            item.get("source") == job.get("source") and item.get("url") == job.get("url")
            for item in sent.values() if isinstance(item, dict)
        )
        if key not in sent and not legacy_match:
            result.append(job)
    return result


def mark_sent(jobs: list[dict], path: Path) -> None:
    sent = load(path)
    stamp = utc_now()
    for job in jobs:
        key = job.get("_key") or job_key(job)
        sent[key] = {"sent_at": stamp, "source": job.get("source", ""), "url": job.get("url", "")}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sent, indent=2, ensure_ascii=False), encoding="utf-8")
