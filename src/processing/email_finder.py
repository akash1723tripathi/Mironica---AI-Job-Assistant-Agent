"""Extract only public, explicitly published email addresses from job pages."""

from __future__ import annotations

import re
import requests
from bs4 import BeautifulSoup

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def discover(jobs: list[dict], limit: int = 15) -> list[dict]:
    for job in jobs[:limit]:
        if job.get("recruiter_email") or not job.get("url", "").startswith("http"):
            continue
        try:
            response = requests.get(job["url"], timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; AIJobAssistant/2.0)"})
            if response.ok:
                text = BeautifulSoup(response.text, "html.parser").get_text(" ")
                match = EMAIL.search(text)
                if match:
                    job["recruiter_email"] = match.group(0)
                    job["email_source"] = "public_job_page"
        except requests.RequestException:
            pass
    return jobs
