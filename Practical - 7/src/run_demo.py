import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
DB_PATH = DATA_DIR / "cdc_demo.db"
OUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS operational_inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cdc_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    product_id INTEGER NOT NULL,
    before_data TEXT,
    after_data TEXT,
    captured_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analytical_inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    updated_at TEXT NOT NULL
);
"""

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def encode(row):
    return json.dumps(dict(row), sort_keys=True) if row is not None else None

def capture_event(conn, operation, product_id, before_data, after_data):
    conn.execute(
        "INSERT INTO cdc_events(operation, product_id, before_data, after_data, captured_at) VALUES (?, ?, ?, ?, ?)",
        (operation, product_id, encode(before_data), encode(after_data), now())
    )

def replay_events(conn):
    events = conn.execute("SELECT * FROM cdc_events ORDER BY event_id").fetchall()
    for event in events:
        op, product_id, after_data = event["operation"], event["product_id"], event["after_data"]
        if op in ("INSERT", "UPDATE"):
            row = json.loads(after_data)
            conn.execute("""
                INSERT INTO analytical_inventory(product_id, product_name, stock_quantity, unit_price, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                  product_name=excluded.product_name,
                  stock_quantity=excluded.stock_quantity,
                  unit_price=excluded.unit_price,
                  updated_at=excluded.updated_at
            """, (row["product_id"], row["product_name"], row["stock_quantity"], row["unit_price"], row["updated_at"]))
        elif op == "DELETE":
            conn.execute("DELETE FROM analytical_inventory WHERE product_id = ?", (product_id,))

def rows_as_dicts(conn, table):
    return [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY product_id").fetchall()]

def main():
    # Reset demo DB each run so the output remains reproducible.
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    print("1) Seed initial operational inventory")
    seed = [
        (101, "Keyboard", 35, 799.00, now()),
        (102, "Mouse", 50, 399.00, now()),
        (103, "Monitor", 12, 8999.00, now()),
    ]
    conn.executemany("INSERT INTO operational_inventory VALUES (?, ?, ?, ?, ?)", seed)
    conn.executemany("INSERT INTO analytical_inventory VALUES (?, ?, ?, ?, ?)", seed)
    conn.commit()
    print("   Seeded 3 products into operational and analytical tables.")

    print("\n2) Apply and capture INSERT")
    inserted = {"product_id": 104, "product_name": "Webcam", "stock_quantity": 20, "unit_price": 1499.00, "updated_at": now()}
    conn.execute("INSERT INTO operational_inventory VALUES (?, ?, ?, ?, ?)", tuple(inserted.values()))
    capture_event(conn, "INSERT", 104, None, inserted)
    conn.commit()
    print("   Captured INSERT for product_id=104 (Webcam).")

    print("\n3) Apply and capture UPDATE")
    before = dict(conn.execute("SELECT * FROM operational_inventory WHERE product_id=102").fetchone())
    conn.execute("UPDATE operational_inventory SET stock_quantity=?, updated_at=? WHERE product_id=?", (42, now(), 102))
    after = dict(conn.execute("SELECT * FROM operational_inventory WHERE product_id=102").fetchone())
    capture_event(conn, "UPDATE", 102, before, after)
    conn.commit()
    print("   Captured UPDATE for product_id=102 (stock quantity changed to 42).")

    print("\n4) Apply and capture DELETE")
    before = dict(conn.execute("SELECT * FROM operational_inventory WHERE product_id=103").fetchone())
    conn.execute("DELETE FROM operational_inventory WHERE product_id=103")
    capture_event(conn, "DELETE", 103, before, None)
    conn.commit()
    print("   Captured DELETE for product_id=103 (Monitor).")

    print("\n5) Replay events in event_id order")
    replay_events(conn)
    conn.commit()

    source = rows_as_dicts(conn, "operational_inventory")
    target = rows_as_dicts(conn, "analytical_inventory")
    events = [dict(r) for r in conn.execute("SELECT * FROM cdc_events ORDER BY event_id").fetchall()]
    passed = source == target

    report = {
        "practical": "Practical 7 — Change Data Capture (CDC)",
        "database": str(DB_PATH.relative_to(ROOT)),
        "events_captured": len(events),
        "operation_counts": {
            op: sum(1 for e in events if e["operation"] == op)
            for op in ["INSERT", "UPDATE", "DELETE"]
        },
        "source_rows": len(source),
        "analytical_rows": len(target),
        "source_matches_analytical": passed,
        "event_ids_in_order": [e["event_id"] for e in events],
        "events": events,
        "operational_inventory": source,
        "analytical_inventory": target,
    }
    (OUT_DIR / "cdc_execution_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    audit_lines = [
        "Practical 7 — CDC execution audit",
        f"Execution time (UTC): {now()}",
        f"Events captured: {len(events)}",
        "Events replayed in ascending event_id order:",
    ]
    audit_lines += [f"event_id={e['event_id']} operation={e['operation']} product_id={e['product_id']} captured_at={e['captured_at']}" for e in events]
    audit_lines += [f"Source rows: {len(source)}", f"Analytical rows: {len(target)}", f"Source matches analytical: {passed}"]
    (OUT_DIR / "cdc_audit.log").write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print("\n6) Verify replication")
    print(f"   Events captured: {len(events)}")
    print(f"   Operation counts: {report['operation_counts']}")
    print(f"   Operational rows: {len(source)} | Analytical rows: {len(target)}")
    print(f"   Source matches analytical: {'PASS' if passed else 'FAIL'}")
    print("\nGenerated:")
    print("   data/cdc_demo.db")
    print("   output/cdc_execution_report.json")
    print("   output/cdc_audit.log")
    conn.close()
    if not passed:
        raise SystemExit("CDC validation failed: source and analytical tables differ.")

if __name__ == "__main__":
    main()
