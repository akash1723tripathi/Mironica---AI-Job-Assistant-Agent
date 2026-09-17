"""
run_scan.py

The Phase-1 daily pipeline. This is what GitHub Actions (or Task Scheduler)
calls at 11 AM. No LinkedIn login involved anywhere in this file -- safe to
run in the cloud.

    scan ATS boards -> drop already-seen jobs -> score eligibility
    -> send new matches to Telegram -> mark them seen

LinkedIn hiring-post monitoring (Phase 2) stays a separate script that runs
locally, because it needs your logged-in session -- merge its output into
data/ats_jobs_raw.json's format if you want it in the same digest later.
"""

from ats_scanner import scan_all
from state_store import filter_new, mark_seen
from eligibility import filter_eligible
from telegram_notify import send_digest


def main():
    print("=" * 50)
    print("DAILY JOB SCAN")
    print("=" * 50)

    raw_jobs = scan_all()

    new_jobs = filter_new(raw_jobs)
    print(f"New (not seen before): {len(new_jobs)} / {len(raw_jobs)}")

    eligible_jobs = filter_eligible(new_jobs)
    print(f"Eligible (score >= 70): {len(eligible_jobs)}")

    send_digest(eligible_jobs)

    # Mark ALL new jobs as seen (not just eligible ones) so a job that
    # scored low today doesn't get re-scored and re-considered tomorrow.
    mark_seen(new_jobs)

    print("Done.")


if __name__ == "__main__":
    main()