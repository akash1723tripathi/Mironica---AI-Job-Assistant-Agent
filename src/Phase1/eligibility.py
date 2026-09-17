"""
eligibility.py

Scores each job 0-100 against Akash's target profile, using the same rubric
from the original problem-statement doc. The difference from the old
enrich_jobs.py: this runs on real description text (ATS APIs return it
directly), so a hard-reject keyword actually has something to match against
instead of silently passing everything through on an empty string.

v1 is regex/keyword based on purpose -- cheap, fast, no API cost. If this
isn't catching enough nuance (e.g. cleverly-worded senior roles), the next
step is routing borderline scores (55-75) through a small LLM call instead
of raising keyword weights further.
"""

import re

REJECT_KEYWORDS = [
    "senior", "sr.", "lead", "staff", "principal", "architect", "manager",
    "java developer", ".net", "dotnet", "android", "flutter", "qa engineer",
    "devops", "ai/ml engineer", "contractor", "freelance", "wordpress", "php developer",
]

SENIOR_EXPERIENCE_PATTERN = re.compile(r"\b([3-9]|\d{2,})\+?\s*(?:-|to)?\s*\d*\s*years?\b", re.I)

SCORING_RULES = [
    # (weight, pattern_list)
    (30, [r"\bbackend\b", r"\bback[- ]end\b", r"\bfull[- ]stack\b", r"\bsoftware engineer\b", r"\bsde\b"]),
    (20, [r"\bnode(\.js)?\b", r"\bexpress(\.js)?\b"]),
    (15, [r"\breact(\.js)?\b", r"\bnext(\.js)?\b"]),
    (15, [r"\bpostgres(ql)?\b", r"\bmongo(db)?\b"]),
    (10, [r"\bfresher\b", r"\bentry[- ]level\b", r"\b0[\s-]*[-to]*\s*[12]\s*years?\b", r"\bnew grad\b"]),
    (10, [r"\b2026\b", r"\bnew grad\b", r"\bcampus\b", r"\bgraduate\b"]),
]

MIN_SCORE_TO_PASS = 70


def is_hard_reject(text: str) -> str | None:
    """Returns the matched reject keyword, or None if the text clears the gate."""
    lower = text.lower()
    for kw in REJECT_KEYWORDS:
        if kw in lower:
            return kw
    # Hard experience gate: anything asking for 3+ years is out regardless of score
    m = SENIOR_EXPERIENCE_PATTERN.search(lower)
    if m:
        return f"experience requirement ({m.group().strip()})"
    return None


def score_job(job: dict) -> dict:
    """Adds 'score' and 'reject_reason' to the job dict, in place, and returns it."""
    full_text = f"{job.get('title','')} {job.get('description','')}"

    reject_reason = is_hard_reject(full_text)
    if reject_reason:
        job["score"] = 0
        job["reject_reason"] = reject_reason
        return job

    lower = full_text.lower()
    score = 0
    for weight, patterns in SCORING_RULES:
        if any(re.search(p, lower) for p in patterns):
            score += weight

    job["score"] = score
    job["reject_reason"] = None
    return job


def filter_eligible(jobs: list) -> list:
    """Scores every job, returns only those at or above MIN_SCORE_TO_PASS, sorted best first."""
    scored = [score_job(j) for j in jobs]
    eligible = [j for j in scored if j["score"] >= MIN_SCORE_TO_PASS]
    eligible.sort(key=lambda j: j["score"], reverse=True)
    return eligible