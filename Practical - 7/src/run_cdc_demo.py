import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
DB = DATA / "cdc_demo.db"
if DB.exists():
    DB.unlink()

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def row_dict(row):
    return dict(row) if row else None

def emit_event(con, operation, product_id, old_data, new_data):
    con.execute(
        "INSERT INTO cdc_events(operation, product_id, old_data, new_data, captured_at) VALUES (?, ?, ?, ?, ?)",
        (operation, product_id, json.dumps(old_data) if old_data is not None else None,
         json.dumps(new_data) if new_data is not None else None, now())
    )

def apply_to_analytics(con, operation, product_id, new_data):
    if operation in ("INSERT", "UPDATE"):
        con.execute("""
            INSERT INTO analytics_inventory(product_id, product_name, stock_quantity, unit_price, source_updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                product_name=excluded.product_name,
                stock_quantity=excluded.stock_quantity,
                unit_price=excluded.unit_price,
                source_updated_at=excluded.source_updated_at
        """, (new_data["product_id"], new_data["product_name"], new_data["stock_quantity"],
              new_data["unit_price"], new_data["updated_at"]))
    elif operation == "DELETE":
        con.execute("DELETE FROM analytics_inventory WHERE product_id = ?", (product_id,))

def main():
    con = connect()
    con.executescript("""
    CREATE TABLE operational_inventory(
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        stock_quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE cdc_events(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation TEXT NOT NULL CHECK(operation IN ('INSERT','UPDATE','DELETE')),
        product_id INTEGER NOT NULL,
        old_data TEXT,
        new_data TEXT,
        captured_at TEXT NOT NULL,
        applied INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE analytics_inventory(
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        stock_quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        source_updated_at TEXT NOT NULL
    );
    """)
    # Seed the source and analytical tables with the same initial snapshot.
    initial = [
        (101, "Keyboard", 35, 799.00),
        (102, "Mouse", 60, 399.00),
        (103, "Monitor", 12, 8999.00),
    ]
    for pid, name, qty, price in initial:
        ts = now()
        con.execute("INSERT INTO operational_inventory VALUES (?, ?, ?, ?, ?)", (pid, name, qty, price, ts))
        con.execute("INSERT INTO analytics_inventory VALUES (?, ?, ?, ?, ?)", (pid, name, qty, price, ts))
    con.commit()
    print("Initial snapshot loaded: 3 rows in source and analytics.")

    # Capture a new INSERT.
    new_row = {"product_id": 104, "product_name": "Webcam", "stock_quantity": 18,
               "unit_price": 1299.00, "updated_at": now()}
    con.execute("INSERT INTO operational_inventory VALUES (?, ?, ?, ?, ?)",
                (new_row["product_id"], new_row["product_name"], new_row["stock_quantity"],
                 new_row["unit_price"], new_row["updated_at"]))
    emit_event(con, "INSERT", 104, None, new_row)
    con.commit()
    print("Captured INSERT: product_id=104 (Webcam)")

    # Capture an UPDATE.
    old = row_dict(con.execute("SELECT * FROM operational_inventory WHERE product_id=102").fetchone())
    updated = dict(old)
    updated["stock_quantity"] = 42
    updated["unit_price"] = 429.00
    updated["updated_at"] = now()
    con.execute("UPDATE operational_inventory SET stock_quantity=?, unit_price=?, updated_at=? WHERE product_id=?",
                (updated["stock_quantity"], updated["unit_price"], updated["updated_at"], 102))
    emit_event(con, "UPDATE", 102, old, updated)
    con.commit()
    print("Captured UPDATE: product_id=102 (Mouse), stock=42, price=429.00")

    # Capture a DELETE.
    old = row_dict(con.execute("SELECT * FROM operational_inventory WHERE product_id=103").fetchone())
    con.execute("DELETE FROM operational_inventory WHERE product_id=103")
    emit_event(con, "DELETE", 103, old, None)
    con.commit()
    print("Captured DELETE: product_id=103 (Monitor)")

    # Replay unapplied events in event_id order; each application and applied marker is atomic.
    events = con.execute("SELECT * FROM cdc_events WHERE applied=0 ORDER BY event_id").fetchall()
    for event in events:
        new_data = json.loads(event["new_data"]) if event["new_data"] else None
        con.execute("BEGIN")
        try:
            apply_to_analytics(con, event["operation"], event["product_id"], new_data)
            con.execute("UPDATE cdc_events SET applied=1 WHERE event_id=?", (event["event_id"],))
            con.commit()
        except Exception:
            con.rollback()
            raise
        print(f"Replayed event #{event['event_id']}: {event['operation']} product_id={event['product_id']}")

    source = [row_dict(r) for r in con.execute("SELECT * FROM operational_inventory ORDER BY product_id")]
    analytics = [row_dict(r) for r in con.execute("SELECT * FROM analytics_inventory ORDER BY product_id")]
    source_state = [{k: r[k] for k in ("product_id","product_name","stock_quantity","unit_price")} for r in source]
    analytic_state = [{k: r[k] for k in ("product_id","product_name","stock_quantity","unit_price")} for r in analytics]
    passed = source_state == analytic_state
    event_rows = [dict(r) for r in con.execute("SELECT * FROM cdc_events ORDER BY event_id")]
    (OUT / "cdc_events.json").write_text(json.dumps(event_rows, indent=2), encoding="utf-8")
    log = [
        "Practical 7 — Change Data Capture (CDC)",
        f"Run time: {now()}",
        "Operations captured: INSERT, UPDATE, DELETE",
        f"Events captured: {len(event_rows)}",
        f"Events applied: {sum(r['applied'] for r in event_rows)}",
        f"Source row count: {len(source)}",
        f"Analytics row count: {len(analytics)}",
        f"Source and analytics state match: {'PASS' if passed else 'FAIL'}",
    ]
    (OUT / "cdc_execution.log").write_text("\\n".join(log) + "\\n", encoding="utf-8")
    print(f"Final source rows: {len(source)}; analytics rows: {len(analytics)}")
    print("Validation:", "PASS" if passed else "FAIL")
    print("Saved output/cdc_events.json and output/cdc_execution.log")
    con.close()
    if not passed:
        raise SystemExit("CDC validation failed")

if __name__ == "__main__":
    main()
