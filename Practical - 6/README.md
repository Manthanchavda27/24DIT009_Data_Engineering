# Practical 6 — Storage Lifecycle Management

## Objective
Implement and test a Hot/Warm/Cold storage lifecycle policy based on object age, last-access date, access frequency, and retention requirements.

## Run on Windows CMD
```cmd
py -m venv .venv
.venv\Scripts\activate
python src\generate_data.py
python src\lifecycle_manager.py
python src\create_report.py
```

Core simulation uses only Python's standard library. Optional MinIO integration can be added separately.

## Output
- `data/operational_logs.csv`
- `data/access_manifest.csv`
- `data/server_audit.csv`
- `output/lifecycle_execution.json`
- `output/lifecycle_audit.log`
- `output/lifecycle_report.md`

Important: this project simulates tier decisions. It does not physically move objects between storage classes or delete expired objects. Estimated cost savings use illustrative rates, not vendor pricing.
