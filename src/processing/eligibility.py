"""
Two-stage hard filtering and profile-based relevance scoring.
Implements exact weighted scoring matrix and tuned Java/seniority rejection rules.
"""

from __future__ import annotations

import re
from .normalize import clean_text

SENIOR = re.compile(
    r"\b(senior|sr\.?|lead|staff|principal|architect|manager|director|head|vice president|vp|avp|sde\s*(ii|iii|iv|2|3|4)|engineer\s*(ii|iii|2|3))\b",
    re.I
)
EXPERIENCE_3PLUS = re.compile(
    r"\b([3-9]|[1-9]\d)\s*(?:\+|[-–—]\s*\d+|to\s+\d+)?\s*years?\b",
    re.I
)
ENTRY = re.compile(
    r"\b(intern|internship|fresher|entry[ -]?level|new grad|graduate|associate|assoc|0\s*[-–—to]*\s*[12]\s*years?|2026)\b",
    re.I
)
TARGET_TITLE = re.compile(
    r"\b(back[ -]?end|software\s*(engineer|developer)|sde|full[ -]?stack|golang?|go\s*(engineer|developer)|assoc\w*\s*software)\b",
    re.I
)
JAVA_PRIMARY_ROLE = re.compile(
    r"^\s*(java\s+(engineer|developer|architect|lead|programmer)|(engineer|developer|programmer)\s*[-:–]\s*java)\b",
    re.I
)
FOREIGN_REMOTE = re.compile(
    r"\b(usa|united states|canada|europe|european union|uk|united kingdom|singapore|australia|new zealand)\b",
    re.I
)
INDIA = re.compile(
    r"\b(india|noida|greater noida|gurugram|gurgaon|bengaluru|bangalore|pune|lucknow|hyderabad|mumbai|delhi|chennai|kolkata)\b",
    re.I
)
PREFERRED_LOCATIONS = re.compile(
    r"\b(noida|greater noida|gurugram|gurgaon|bengaluru|bangalore|pune|lucknow)\b",
    re.I
)


def hard_reject(job: dict) -> str:
    title = clean_text(job.get("title"))
    description = clean_text(job.get("description"))
    combined = clean_text(" ".join([title, description, job.get("experience", ""), job.get("employment_type", "")]))
    location = clean_text(job.get("location"))

    # 1. Seniority Check (Title or explicit requirements)
    if SENIOR.search(title) or SENIOR.search(combined[:300]):
        return "seniority above entry level"

    # 2. Experience Check (3+ years requirement)
    if EXPERIENCE_3PLUS.search(combined):
        return "experience requirement of 3+ years"

    # 3. Primary Java Role Check (Reject only when Java is primary role in Title)
    if JAVA_PRIMARY_ROLE.search(title):
        return "primary java role"

    # 4. Foreign Remote Restriction Check
    if "remote" in location.lower() and FOREIGN_REMOTE.search(location + " " + combined[:300]) and not INDIA.search(location + " " + combined[:300]):
        return "remote role restricted outside India"

    # 5. Target Title / Role Family Check
    if not TARGET_TITLE.search(title) and not TARGET_TITLE.search(combined[:300]):
        return "non-target role family"

    return ""


def score(job: dict) -> int:
    title = clean_text(job.get("title")).lower()
    description = clean_text(job.get("description")).lower()
    combined = f"{title} {description}"
    location = clean_text(job.get("location")).lower()
    total = 0

    # 1. Target Title Match (25 pts)
    if TARGET_TITLE.search(title):
        total += 25

    # 2. Entry / Associate / New Grad / Intern / Fresher Signal (20 pts)
    if ENTRY.search(title) or ENTRY.search(combined[:300]):
        total += 20

    # 3. Node.js / TypeScript / Go (20 pts)
    if any(x in combined for x in ("node", "nodejs", "node.js", "typescript", "ts", "express", "go", "golang")):
        total += 20

    # 4. React / Next.js (10 pts)
    if any(x in combined for x in ("react", "react.js", "reactjs", "next.js", "nextjs", "next")):
        total += 10

    # 5. MongoDB / PostgreSQL / SQL (10 pts)
    if any(x in combined for x in ("mongo", "mongodb", "postgres", "postgresql", "sql", "prisma", "redis")):
        total += 10

    # 6. Preferred Location (Noida, Gurugram, Bengaluru, Pune, Lucknow) (10 pts)
    if PREFERRED_LOCATIONS.search(location) or PREFERRED_LOCATIONS.search(title):
        total += 10

    # 7. India Remote (5 pts)
    if "remote" in location and ("india" in location or "remote" in location):
        total += 5

    return total


def evaluate(job: dict, minimum_score: int = 50) -> dict:
    reason = hard_reject(job)
    job["reject_reason"] = reason
    job["score"] = 0 if reason else score(job)
    if not reason and job["score"] < minimum_score:
        job["reject_reason"] = f"score below minimum ({minimum_score})"
    return job
