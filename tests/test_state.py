import json
import pytest
from pathlib import Path
from src.processing.state import filter_unsent, mark_sent, load

def test_sent_state_flow(tmp_path: Path):
    state_file = tmp_path / "sent_jobs.json"
    
    jobs = [
        {"source": "greenhouse", "title": "SDE 1", "company": "Co A", "url": "https://coA.com/job/1", "_key": "key1"},
        {"source": "lever", "title": "SDE 2", "company": "Co B", "url": "https://coB.com/job/2", "_key": "key2"}
    ]

    # Filter with empty state
    unsent = filter_unsent(jobs, state_file)
    assert len(unsent) == 2

    # Mark first job as sent
    mark_sent([jobs[0]], state_file)

    # Filter again
    unsent2 = filter_unsent(jobs, state_file)
    assert len(unsent2) == 1
    assert unsent2[0]["_key"] == "key2"
