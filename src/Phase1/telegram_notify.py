"""
telegram_notify.py

Sends the daily digest to Telegram. Needs two environment variables:

  TELEGRAM_BOT_TOKEN  -> from @BotFather when you create the bot
  TELEGRAM_CHAT_ID    -> your personal chat id (message the bot once, then
                          visit https://api.telegram.org/bot<TOKEN>/getUpdates
                          to read your chat id from the response)

Keep these out of git -- put them in a .env file (already have python-dotenv?
`pip install python-dotenv` if not) or set them as GitHub Actions secrets.
"""

import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def format_job_message(job: dict) -> str:
    desc = (job.get("description", "") or "").strip()
    # strip any leftover HTML tags from Greenhouse/Lever rich text
    desc = desc.replace("<p>", "").replace("</p>", " ").replace("<br>", " ")
    desc_short = " ".join(desc.split())[:150]

    email_line = f"\n📩 Recruiter Email: {job['recruiter_email']}" if job.get("recruiter_email") else ""

    return (
        f"🏢 Company: {job.get('company','').title()}\n"
        f"💼 Role: {job.get('title','')}\n"
        f"📝 Description: {desc_short}...\n"
        f"🎯 Match: {job.get('score', 0)}%\n"
        f"📍 Location: {job.get('location','Not specified')}"
        f"{email_line}\n"
        f"🔗 Apply: {job.get('url','')}\n"
        f"📄 Source: {job.get('source','')}"
    )


def send_digest(jobs: list):
    if not BOT_TOKEN or not CHAT_ID:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — printing digest instead:\n")
        for job in jobs:
            print(format_job_message(job))
            print("-" * 40)
        return

    if not jobs:
        text = "No new matching jobs today. 🔍"
        _send(text)
        return

    header = f"🔔 {len(jobs)} new job match(es) today\n\n"
    _send(header.rstrip())

    for job in jobs[:20]:  # cap at 20/day per the original spec
        _send(format_job_message(job))


def _send(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=15)
        if r.status_code != 200:
            print(f"Telegram send failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Telegram send error: {e}")