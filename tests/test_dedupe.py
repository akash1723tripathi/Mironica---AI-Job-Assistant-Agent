import pytest
from src.processing.dedupe import dedupe, job_key, get_source_priority

def test_source_priority():
    assert get_source_priority("linkedin_jobs") > get_source_priority("greenhouse")
    assert get_source_priority("greenhouse") > get_source_priority("workday")
    assert get_source_priority("workday") > get_source_priority("linkedin_posts")

def test_dedupe_same_url():
    jobs = [
        {"source": "linkedin_posts", "company": "Acme", "title": "SDE", "url": "https://company.com/jobs/1", "score": 60},
        {"source": "greenhouse", "company": "Acme", "title": "SDE", "url": "https://company.com/jobs/1", "score": 80}
    ]
    unique = dedupe(jobs)
    assert len(unique) == 1
    assert unique[0]["source"] == "greenhouse"

def test_dedupe_company_title_priority():
    jobs = [
        {"source": "linkedin_posts", "company": "Razorpay", "title": "Backend Engineer", "url": "https://post.com/1", "score": 70},
        {"source": "linkedin_jobs", "company": "Razorpay", "title": "Backend Engineer", "url": "https://linkedin.com/jobs/1", "score": 75}
    ]
    unique = dedupe(jobs)
    assert len(unique) == 1
    assert unique[0]["source"] == "linkedin_jobs"
