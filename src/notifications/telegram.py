"""
Telegram delivery with explicit success/failure semantics.
Formats qualified jobs with 2-line descriptions, match score, and direct apply links.
"""

from __future__ import annotations

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("telegram_notify")


def format_job(job: dict) -> str:
    title = job.get("title", "Software Engineer")
    company = job.get("company", "Tech Company")
    location = job.get("location", "India / Remote")
    score = job.get("score", 0)
    url = job.get("url", "")
    post_url = job.get("post_url", "")
    email = job.get("recruiter_email", "")
    contact_type = job.get("contact_type", "") or ("form" if url else "email_only" if email else "post_only")

    # Clean description for 2-line summary (~180 chars)
    desc = " ".join(str(job.get("description", "")).split())
    summary = desc[:180] + "..." if len(desc) > 180 else (desc or "Fresh Software Engineering opportunity.")

    lines = [
        f"🟢 {title}",
        f"🏢 {company}",
        f"📍 {location}",
        f"📝 {summary}",
        f"🎯 Match: {score}%",
    ]

    if contact_type == "form":
        # Real apply link known — this is the main action.
        lines.append(f"🔗 Apply: {url}")
        if post_url:
            lines.append(f"📄 Original post: {post_url}")
    elif contact_type == "email_only":
        # No apply link, but a recruiter email was found — cold mail is the next step.
        lines.append(f"📧 Cold mail needed: {email}")
        if post_url:
            lines.append(f"📄 Post: {post_url}")
    elif contact_type == "post_only":
        # Neither an apply link nor an email — just the post, Akash reviews it himself.
        lines.append("⚠️ No form/email found — review the post")
        lines.append(f"📄 Post: {post_url or url}")
    else:
        # Fallback for any job that somehow has none of the usual fields.
        if email:
            lines.append(f"📧 Recruiter: {email}")
        if url or post_url:
            lines.append(f"🔗 Link: {url or post_url}")

    return "\n".join(lines)


def _send(text: str) -> bool:
    token, chat_id = os.getenv("BOT_TOKEN"), os.getenv("CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("BOT_TOKEN or CHAT_ID environment variables are missing")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }

    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API rejected request: {body}")
    return True


def send_digest(jobs: list[dict], limit: int = 10) -> list[dict]:
    if not jobs:
        logger.info("No qualified jobs to deliver to Telegram.")
        return []

    selected = jobs[:limit]
    header = f"🚀 AI Job Assistant Digest\n\nFound {len(selected)} high-quality fresh opportunities today."
    
    try:
        _send(header)
        sent = []
        for job in selected:
            msg = format_job(job)
            _send(msg)
            sent.append(job)
        return sent
    except Exception as exc:
        logger.error(f"Telegram notification delivery error: {exc}")
        raise
