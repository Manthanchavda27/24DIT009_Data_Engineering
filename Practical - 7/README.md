# Practical 7 — Change Data Capture (CDC)

## Objective
Simulate incremental capture of INSERT, UPDATE, and DELETE changes from an operational inventory database, append each mutation to an audit ledger, and replay those events into an analytical table.

## Requirements
- Python 3.10+
- No third-party packages required for the included SQLite-based runnable demo.
- The practical index names PostgreSQL, Psycopg2, PL/pgSQL event logs, and replication loops as the target technologies. This ZIP provides a reliable local SQLite simulation first; PostgreSQL integration can be added as an extension.

## Run on Windows CMD
```cmd
py -m venv .venv
.venv\Scripts\activate
python src\run_demo.py
```

## What the demo does
1. Creates an operational inventory table and an analytical replica.
2. Applies INSERT, UPDATE, and DELETE operations.
3. Captures each change into a durable `cdc_events` audit ledger with a monotonically increasing event ID.
4. Replays events to the analytical table in event order.
5. Verifies the analytical table matches the operational source after replication.
6. Writes a JSON execution report and a readable audit log to `output/`.

## Important
This is a local educational simulation of CDC, not a production-grade log-based CDC connector. The events are captured by the Python demo as it performs each mutation. It demonstrates incremental change capture and ordered replay without full-table dumps.
