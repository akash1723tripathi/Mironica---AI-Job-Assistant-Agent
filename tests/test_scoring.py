import pytest
from src.processing.eligibility import score, hard_reject, evaluate

def test_target_title_scoring():
    job = {
        "title": "Backend Engineer",
        "description": "Looking for a Node.js and TypeScript developer in Noida",
        "location": "Noida, India"
    }
    s = score(job)
    assert s >= 50
    assert hard_reject(job) == ""

def test_entry_level_scoring():
    job = {
        "title": "Associate Software Engineer",
        "description": "Fresher or 0-1 year experience in Go and PostgreSQL",
        "location": "Bengaluru, India"
    }
    res = evaluate(job, minimum_score=50)
    assert res["score"] >= 50
    assert res["reject_reason"] == ""

def test_seniority_hard_reject():
    job = {
        "title": "Senior Software Engineer",
        "description": "Requires 5+ years experience in Node.js",
        "location": "Remote"
    }
    assert hard_reject(job) != ""

def test_experience_hard_reject():
    job = {
        "title": "Software Engineer",
        "description": "Minimum 4+ years of experience required",
        "location": "Gurugram"
    }
    assert hard_reject(job) != ""

def test_java_secondary_not_rejected():
    job = {
        "title": "Backend Engineer",
        "description": "Must know Node.js or TypeScript. Knowledge of Java is a plus.",
        "location": "Noida"
    }
    assert hard_reject(job) == ""
    assert score(job) >= 50

def test_java_primary_rejected():
    job = {
        "title": "Java Developer",
        "description": "Primary Java backend development role",
        "location": "Pune"
    }
    assert hard_reject(job) == "primary java role"
