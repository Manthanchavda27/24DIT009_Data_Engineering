# Practical 11 — Data Serving, Reverse ETL, and Security

## Objective
Demonstrate a secure analytics serving workflow using synthetic customer analytics data. The program tokenizes identity fields with SHA-256, masks emails in analyst-facing output, enforces simulated analyst/admin role permissions, syncs approved metrics to an operational destination table, and records audit events.

## Windows CMD
```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python src\run_practical.py
```

## Features
- Synthetic customer analytics: email, segment, churn score, purchase metric.
- SHA-256 identity hashing (deterministic pseudonymous token, not encryption).
- Email masking for analyst role.
- Role-based access control simulation: analyst sees masked/tokenized fields; admin sees the full synthetic record.
- Reverse ETL: approved segment and churn metric are written into an operational-style SQLite table.
- Central audit log records access and sync actions.
- SQLite database and sample output logs.

## Output
- `data/secure_serving.db`
- `output/analyst_view.csv`
- `output/reverse_etl_sync.csv`
- `output/audit.log`
- `output/practical_report.md`

## Security notes
SHA-256 hashing is not encryption and cannot be reversed like encrypted data. Email hashes can still be vulnerable to guessing attacks; use keyed HMAC or a vetted tokenization service for production. This lab simulates RBAC in Python; a production deployment should also enforce database-level permissions and use managed encryption keys. The Reverse ETL operation here is a local SQLite demonstration, not a live Airbyte/Meltano integration.
