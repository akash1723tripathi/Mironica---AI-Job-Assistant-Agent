# AI Job Assistant — Automated Job Discovery & Delivery Engine

An automated, production-ready AI Job Assistant designed to discover real fresher and early-career software engineering opportunities (Backend, SDE, Full Stack, Associate) from multiple public sources every morning at 11:00 AM IST and deliver qualified jobs directly to Telegram.

---

## Highlights & Specifications

- **100+ Validated ATS Companies**: Automated registry builder covering Greenhouse, Lever, Ashby, Workday, and Zoho Recruit.
- **Multi-Source Scraping**: Collects opportunities from LinkedIn Jobs, LinkedIn Hiring Posts, Greenhouse, Lever, Ashby, Workday, and YC Work at a Startup.
- **Playwright Automation**: YC collector rewritten with Playwright (bypassing HTTP 406 anti-bot protections).
- **Exact Weighted Scoring**: Evaluates target roles, tech stack, entry-level signals, and preferred location. Rejects senior roles (3+ yrs exp) and primary Java roles while retaining secondary Java mentions.
- **Source Priority Deduplication**: Multi-signal deduplication preserving higher-priority sources (`LinkedIn Job > Greenhouse > Workday > Career Page > Hiring Post`).
- **0 Duplicate Delivery Guarantee**: Sent-job state store in `data/state/sent_jobs.json`.
- **Quality Metrics Reports**: Generates `data/reports/quality_report.md` and `data/reports/run_report.json` after every run.

---

## Quick Start

### 1. Installation

```bash
git clone https://github.com/akash1723tripathi/Job-Assistant---AI-Agent.git
cd Job-Assistant---AI-Agent
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

### 3. Build & Verify Registry

```bash
python src/registry/build_registry.py --verify
```

### 4. Collector Smoke Tests

Test any collector independently:

```bash
python -m src.collectors.linkedin_jobs --test
python -m src.collectors.linkedin_posts --test
python -m src.collectors.ats --test
python -m src.collectors.workday --test
python -m src.collectors.yc --test
```

### 5. Run Full Pipeline

```bash
# Dry Run (Scrapes, scores, deduplicates, and generates quality report without sending Telegram)
python src/run_pipeline.py --dry-run

# Live Production Run
python src/run_pipeline.py
```

### 6. Run Test Suite

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
AI-Job-Assistant/
├── config/
│   ├── profile.json
│   ├── search.json
│   ├── sources.seed.json
│   └── sources.generated.json
├── data/
│   ├── raw/
│   ├── processed/
│   ├── reports/
│   │   ├── registry_report.json
│   │   ├── run_report.json
│   │   └── quality_report.md
│   └── state/
│       └── sent_jobs.json
├── src/
│   ├── collectors/
│   │   ├── ats.py
│   │   ├── career_pages.py
│   │   ├── linkedin_jobs.py
│   │   ├── linkedin_posts.py
│   │   ├── workday.py
│   │   ├── yc.py
│   │   └── zoho_recruit.py
│   ├── processing/
│   │   ├── dedupe.py
│   │   ├── eligibility.py
│   │   ├── email_finder.py
│   │   ├── normalize.py
│   │   └── state.py
│   ├── registry/
│   │   ├── build_registry.py
│   │   └── seed_companies.py
│   ├── notifications/
│   │   └── telegram.py
│   └── run_pipeline.py
├── docs/
│   ├── architecture.md
│   ├── automation.md
│   └── registry.md
├── tests/
│   ├── test_scoring.py
│   ├── test_dedupe.py
│   ├── test_normalize.py
│   ├── test_state.py
│   └── test_registry.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Documentation

- [Architecture & System Flow](docs/architecture.md)
- [Daily Automation Guide](docs/automation.md)
- [Registry Builder & Verification](docs/registry.md)
