from pathlib import Path
import hashlib
import json
import logging
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "output"
DB = DATA / "secure_serving.db"


def sha256_identity(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    visible = local[:1] if local else "*"
    return f"{visible}***@{domain}"


def main():
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    log_path = OUT / "audit.log"
    if log_path.exists():
        log_path.unlink()
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(message)s")

    customers = pd.DataFrame([
        {"customer_id":"C001","email":"riya.shah@example.com","segment":"high_value","churn_score":0.12,"purchase_total":18450.0},
        {"customer_id":"C002","email":"arjun.patel@example.com","segment":"at_risk","churn_score":0.81,"purchase_total":3900.0},
        {"customer_id":"C003","email":"meera.desai@example.com","segment":"loyal","churn_score":0.08,"purchase_total":12600.0},
        {"customer_id":"C004","email":"kabir.mehta@example.com","segment":"at_risk","churn_score":0.74,"purchase_total":2700.0},
        {"customer_id":"C005","email":"nisha.trivedi@example.com","segment":"high_value","churn_score":0.19,"purchase_total":22100.0},
    ])
    customers["identity_sha256"] = customers["email"].apply(sha256_identity)
    customers["email_masked"] = customers["email"].apply(mask_email)

    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE analytics_customers (
            customer_id TEXT PRIMARY KEY, email TEXT NOT NULL,
            identity_sha256 TEXT NOT NULL, segment TEXT NOT NULL,
            churn_score REAL NOT NULL, purchase_total REAL NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE operational_customer_metrics (
            customer_id TEXT PRIMARY KEY, segment TEXT NOT NULL,
            churn_score REAL NOT NULL, synced_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE audit_events (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_role TEXT, action TEXT, record_count INTEGER,
            outcome TEXT, details TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.executemany(
        "INSERT INTO analytics_customers VALUES (?, ?, ?, ?, ?, ?)",
        customers[["customer_id","email","identity_sha256","segment","churn_score","purchase_total"]].itertuples(index=False, name=None)
    )
    con.commit()

    # Simulated RBAC: analyst receives only masked/tokenized identity fields.
    analyst_view = customers[["customer_id","email_masked","identity_sha256","segment","churn_score","purchase_total"]].copy()
    analyst_view = analyst_view.rename(columns={"email_masked":"email"})
    analyst_view.to_csv(OUT / "analyst_view.csv", index=False)
    con.execute("INSERT INTO audit_events(actor_role, action, record_count, outcome, details) VALUES (?, ?, ?, ?, ?)",
                ("analyst","READ_ANALYST_VIEW",len(analyst_view),"SUCCESS","Returned masked email and SHA-256 token only"))
    logging.info("actor=analyst action=READ_ANALYST_VIEW rows=%d outcome=SUCCESS", len(analyst_view))

    # Reverse ETL: sync only approved metrics, not raw email.
    sync = customers[["customer_id","segment","churn_score"]].copy()
    sync.to_csv(OUT / "reverse_etl_sync.csv", index=False)
    con.executemany(
        "INSERT OR REPLACE INTO operational_customer_metrics(customer_id, segment, churn_score) VALUES (?, ?, ?)",
        sync.itertuples(index=False, name=None)
    )
    con.execute("INSERT INTO audit_events(actor_role, action, record_count, outcome, details) VALUES (?, ?, ?, ?, ?)",
                ("reverse_etl","SYNC_CUSTOMER_METRICS",len(sync),"SUCCESS","Synced segment and churn score; no email field"))
    logging.info("actor=reverse_etl action=SYNC_CUSTOMER_METRICS rows=%d outcome=SUCCESS", len(sync))

    # Demonstrate a denied request for raw email by analyst role.
    con.execute("INSERT INTO audit_events(actor_role, action, record_count, outcome, details) VALUES (?, ?, ?, ?, ?)",
                ("analyst","READ_RAW_EMAIL","0","DENIED","Analyst role is not permitted to read raw identity columns"))
    logging.warning("actor=analyst action=READ_RAW_EMAIL rows=0 outcome=DENIED")

    con.commit()
    counts = {
        "analytics_customers": con.execute("SELECT COUNT(*) FROM analytics_customers").fetchone()[0],
        "operational_customer_metrics": con.execute("SELECT COUNT(*) FROM operational_customer_metrics").fetchone()[0],
        "audit_events": con.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0],
    }
    audit = pd.read_sql_query("SELECT * FROM audit_events ORDER BY audit_id", con)
    audit.to_csv(OUT / "audit_records.csv", index=False)
    con.close()

    report = f"""# Practical 11 — Data Serving, Reverse ETL, and Security

## Execution summary
- Synthetic customer rows: {len(customers)}
- Rows in analyst-safe view: {len(analyst_view)}
- Reverse ETL metrics synchronized: {len(sync)}
- Audit records written: {counts['audit_events']}

## Security controls demonstrated
1. **SHA-256 identity hashing:** stores a deterministic hash token for identity matching. Hashing is not encryption.
2. **Masking:** analyst-facing output masks email local parts.
3. **RBAC simulation:** analyst role receives masked/tokenized fields; raw email access is logged as denied.
4. **Reverse ETL:** segment and churn score are synchronized to an operational-style SQLite table without copying email.
5. **Audit logging:** successful reads, syncs, and denied access are recorded.

## Data serving patterns
- **Direct views:** consumers query database views; simple, but can couple consumers to the source database.
- **Virtualization layer:** presents data from multiple sources through one logical access layer; flexible but may add runtime latency.
- **Precomputed data marts:** prepared datasets serve predictable queries quickly but require refresh and storage management.

## Privacy caveats
SHA-256 is a one-way hash, not column-level encryption. Hashing plain email addresses is vulnerable to guessing because emails have limited possible values. Production systems should consider keyed HMAC or managed tokenization, encryption at rest/in transit, managed keys, and actual database permissions.

## Table counts
```json
{json.dumps(counts, indent=2)}
```

## Outputs
- `analyst_view.csv`: masked/tokenized output.
- `reverse_etl_sync.csv`: approved metrics sent to operational destination.
- `audit.log` and `audit_records.csv`: operational audit trail.
- `data/secure_serving.db`: SQLite demonstration database.

## Limitation
This is a local SQLite/Python demonstration of security controls and Reverse ETL concepts, not a live Airbyte/Meltano integration. The role restriction is simulated in the application; production access must be enforced by the database/platform itself.
"""
    (OUT / "practical_report.md").write_text(report, encoding="utf-8")
    print("Practical 11 completed successfully.")
    print(f"Analytics customers: {counts['analytics_customers']}")
    print(f"Operational metrics synced: {counts['operational_customer_metrics']}")
    print(f"Audit events: {counts['audit_events']}")
    print("Analyst raw-email request: DENIED (logged)")
    print("\nGenerated files:")
    for name in ["analyst_view.csv","reverse_etl_sync.csv","audit.log","audit_records.csv","practical_report.md"]:
        print(f"  output\\{name}")


if __name__ == "__main__":
    main()
