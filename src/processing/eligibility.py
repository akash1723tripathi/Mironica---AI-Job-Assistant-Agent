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
# Broad, explicit non-India country/region names, region labels, and major foreign tech-hub
# cities as seen in free-text location fields — "Remote - Poland", "Home based - Worldwide",
# "Toronto, Canada", or just "San Francisco, New York City" with no country at all. Word-
# boundaried so "US" doesn't match inside unrelated words, but still catches bare "US"/"UK".
FOREIGN_REMOTE = re.compile(
    r"\b("
    r"usa|u\.s\.a\.?|us|u\.s\.?|united states|canada|"
    r"europe|european union|eu|uk|u\.k\.?|united kingdom|great britain|"
    r"ireland|germany|france|spain|portugal|italy|netherlands|belgium|"
    r"poland|romania|ukraine|switzerland|sweden|norway|denmark|finland|austria|"
    r"greece|hungary|czech republic|czechia|"
    r"singapore|australia|new zealand|japan|china|hong kong|south korea|korea|"
    r"philippines|indonesia|malaysia|thailand|vietnam|"
    r"mexico|brazil|argentina|chile|colombia|"
    r"south africa|nigeria|egypt|kenya|"
    r"uae|united arab emirates|dubai|saudi arabia|qatar|israel|"
    # Region/coverage labels companies use instead of a country name
    r"worldwide|americas|emea|apac|home\s*based|"
    # Major non-India tech-hub cities that often appear with no country suffix at all
    r"san francisco|new york( city)?|seattle|austin|boston|chicago|los angeles|"
    r"toronto|vancouver|london|berlin|dublin|amsterdam|paris|sydney|melbourne|"
    r"tokyo|tel aviv|prague"
    r")\b",
    re.I
)
INDIA = re.compile(
    r"\b(india|noida|greater noida|gurugram|gurgaon|bengaluru|bangalore|pune|lucknow|hyderabad|mumbai|delhi|chennai|kolkata|kanpur)\b",
    re.I
)
PREFERRED_LOCATIONS = re.compile(
    r"\b(noida|greater noida|gurugram|gurgaon|bengaluru|bangalore|pune|lucknow)\b",
    re.I
)
# Short/ambiguous tech tokens ("go", "ts") need real word boundaries, or they match
# substrings inside unrelated words ("going", "ongoing", "tests", "parts", "charts").
# Bare "go" is still skipped even with \b, since "go-getter"/"go above" would match it —
# only unambiguous Go-language phrasing counts.
NODE_TS_GO = re.compile(
    r"\b(node(\.js)?|node js|typescript|express(\.js)?|"
    r"golang|goroutine|go\s*(lang|routine|module)|go\s+(developer|engineer|programming|microservice))\b",
    re.I
)
REACT_NEXT = re.compile(r"\b(react(\.js)?|reactjs|next(\.js)?|nextjs)\b", re.I)
DB_STACK = re.compile(r"\b(mongo(db)?|postgres(ql)?|sql|prisma|redis)\b", re.I)


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

    # 4. Foreign Location Restriction Check (remote AND onsite/hybrid)
    # Only the location string decides this — a foreign city/company name mentioned in the
    # description (e.g. "our Berlin office") must not falsely reject an India-based role.
    # Not gated on the word "remote": a plain onsite foreign posting ("Toronto, Canada",
    # "Mexico City, Mexico") needs rejecting just as much as a foreign remote one.
    if FOREIGN_REMOTE.search(location) and not INDIA.search(location):
        return "location outside India"

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
    if NODE_TS_GO.search(combined):
        total += 20

    # 4. React / Next.js (10 pts)
    if REACT_NEXT.search(combined):
        total += 10

    # 5. MongoDB / PostgreSQL / SQL (10 pts)
    if DB_STACK.search(combined):
        total += 10

    # 6. Preferred Location (Noida, Gurugram, Bengaluru, Pune, Lucknow) (10 pts)
    if PREFERRED_LOCATIONS.search(location) or PREFERRED_LOCATIONS.search(title):
        total += 10

    # 7. India Remote (5 pts) — only for a remote role that is explicitly India-based or
    # has no foreign country attached (hard_reject already drops the clearly-foreign ones,
    # so anything reaching here with "remote" is India-safe; this just rewards explicit India).
    if "remote" in location and INDIA.search(location):
        total += 5

    return total


def evaluate(job: dict, minimum_score: int = 50) -> dict:
    reason = hard_reject(job)
    job["reject_reason"] = reason
    job["score"] = 0 if reason else score(job)
    if not reason and job["score"] < minimum_score:
        job["reject_reason"] = f"score below minimum ({minimum_score})"
    return job
