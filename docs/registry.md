# ATS Registry Builder & Verification Guide

The Registry Builder manages and validates ATS job boards across Greenhouse, Lever, Ashby, Workday, and Zoho Recruit.

## Usage Modes

### 1. Build / Refresh Registry

Scans the seed catalog, verifies board endpoints, and updates `config/sources.generated.json`:

```bash
python src/registry/build_registry.py
```

### 2. Verify Registry (Mandatory Verification)

Validates all seed and generated ATS boards, generates `data/reports/registry_report.json`, and verifies the 100+ active boards requirement:

```bash
python src/registry/build_registry.py --verify
```

## Generated Artifacts

- `config/sources.seed.json`: Manually maintained company seed list.
- `config/sources.generated.json`: Auto-discovered & validated active ATS boards.
- `data/reports/registry_report.json`: Verification report detailing:
  - Total companies scanned
  - Valid vs. dead boards
  - Newly added & removed companies
  - Provider breakdown (Greenhouse, Lever, Ashby, Workday, Zoho)
  - Validation failure reasons
