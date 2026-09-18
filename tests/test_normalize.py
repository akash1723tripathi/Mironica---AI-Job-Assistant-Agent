import pytest
from src.processing.normalize import new_job, clean_text, clean_url, normalize

def test_clean_text():
    assert clean_text("  Software   Engineer  \n ") == "Software Engineer"
    assert clean_text(None) == ""

def test_clean_url():
    assert clean_url("HTTPS://EXAMPLE.COM/jobs/1/") == "https://example.com/jobs/1"
    assert clean_url("") == ""

def test_new_job_contract():
    job = new_job("test_src", title="Dev", company="Test Corp", url="https://test.com/1/")
    assert job["source"] == "test_src"
    assert job["title"] == "Dev"
    assert job["company"] == "Test Corp"
    assert job["url"] == "https://test.com/1"
    assert "reject_reason" in job
    assert "score" in job

def test_normalize():
    raw = {"source": "greenhouse", "title": "SDE", "url": "https://boards.greenhouse.io/co/jobs/123"}
    norm = normalize(raw)
    assert norm["source"] == "greenhouse"
    assert norm["source_id"] == "https://boards.greenhouse.io/co/jobs/123"
