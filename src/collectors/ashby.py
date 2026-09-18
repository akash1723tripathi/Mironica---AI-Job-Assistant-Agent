"""
Ashby ATS collector — thin wrapper around src.collectors.ats.
Supports standalone `--test` execution via `python -m src.collectors.ashby --test`.
"""

from __future__ import annotations

import sys
import json
import time
import argparse
import logging
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.collectors.ats import collect, fetch_single_board  # noqa: F401  (re-export for pipeline)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ashby_collector")

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ashby Jobs Collector")
    parser.add_argument("--test", action="store_true", help="Run independent collector smoke test")
    args = parser.parse_args()

    start_time = time.time()
    errors = 0
    scanned_companies: set[str] = set()

    sources_gen = ROOT / "config" / "sources.generated.json"
    sources_seed = ROOT / "config" / "sources.seed.json"

    boards: list[dict] = []
    for path in (sources_gen, sources_seed):
        if path.exists():
            with open(path, encoding="utf-8") as f:
                boards.extend(json.load(f).get("ats_boards", []))

    # Deduplicate
    seen: set[tuple] = set()
    dedup: list[dict] = []
    for b in boards:
        key = (b.get("company"), b.get("platform"))
        if key not in seen:
            seen.add(key)
            dedup.append(b)

    try:
        jobs, failures = collect(dedup, platform="ashby")
        for j in jobs:
            if j.get("company"):
                scanned_companies.add(j["company"])
        errors = len(failures)
    except Exception as exc:
        logger.error(f"Ashby test failed: {exc}")
        jobs = []
        errors += 1

    exec_time = round(time.time() - start_time, 2)
    report = {
        "collector": "Ashby",
        "companies_scanned": len(scanned_companies),
        "jobs_collected": len(jobs),
        "accepted": len(jobs),
        "rejected": 0,
        "execution_time_sec": exec_time,
        "errors": errors,
    }
    print("\n--- Ashby Collector Smoke Test Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
