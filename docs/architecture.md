# AI Job Assistant — System Architecture

The AI Job Assistant is an automated pipeline that discovers fresh Software Engineering, Backend, Full Stack, SDE, and Associate opportunities every morning and notifies qualified candidates via Telegram.

## System Architecture Diagram

```
[Registry Builder] (src/registry/build_registry.py)
       │
       ├── Probe ATS APIs (Greenhouse, Lever, Ashby, Workday, Zoho)
       ├── Populate config/sources.generated.json
       └── Verify & generate data/reports/registry_report.json
       │
       ▼
[Pipeline Orchestrator] (src/run_pipeline.py)
       │
       ├── Merge config/sources.seed.json + config/sources.generated.json
       │
       ├──► [Collectors] (Parallel & Dedicated Scraping)
       │      ├── LinkedIn Jobs (Guest API + Playwright)
       │      ├── LinkedIn Posts (Playwright + session state)
       │      ├── ATS Boards (Greenhouse/Lever/Ashby REST APIs)
       │      ├── Workday (JSON Search API)
       │      └── YC (Playwright DOM Parser)
       │
       ├──► [Normalizer] (Canonical schema transformation)
       │
       ├──► [Scoring & Eligibility] (Two-stage hard reject + match scoring)
       │
       ├──► [Deduplication] (Multi-signal hash + source priority ordering)
       │
       ├──► [State Store] (Persistent sent-state in data/state/sent_jobs.json)
       │
       ├──► [Reports Generator]
       │      ├── data/reports/run_report.json
       │      └── data/reports/quality_report.md
       │
       └──► [Telegram Delivery] (10-job digest to channel/bot)
```

## Key Modules

| Path | Purpose |
|---|---|
| `src/registry/build_registry.py` | ATS board discovery and mandatory `--verify` reporting |
| `src/collectors/` | Independent scrapers with `--test` CLI smoke test support |
| `src/processing/eligibility.py` | Profile match scoring & hard rejection engine |
| `src/processing/dedupe.py` | URL/hash deduplication with source priority ordering |
| `src/processing/state.py` | Sent-job state manager preventing duplicate notifications |
| `src/notifications/telegram.py` | Clean digest formatting & Telegram Bot API integration |
| `src/run_pipeline.py` | Main orchestrator & quality metrics generator |
