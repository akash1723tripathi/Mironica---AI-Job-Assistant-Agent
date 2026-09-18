import json
import pytest
from pathlib import Path
from src.registry.build_registry import validate_greenhouse, validate_entry

def test_validate_greenhouse():
    # Razorpay is known active
    valid, reason, count = validate_greenhouse("razorpaysoftwareprivatelimited")
    assert valid is True
    assert count > 0

def test_validate_entry_invalid():
    entry = {"company": "NonExistentCompany999", "platform": "greenhouse", "token": "nonexistentcompany999_xyz_invalid"}
    res = validate_entry(entry)
    assert res["valid"] is False
    assert "HTTP 404" in res["reason"] or "404" in res["reason"]
