import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
events = json.loads((OUT / "cdc_events.json").read_text(encoding="utf-8"))
log = (OUT / "cdc_execution.log").read_text(encoding="utf-8").splitlines()
ops = {}
for e in events:
    ops[e["operation"]] = ops.get(e["operation"], 0) + 1
lines = [
    "# Practical 7 — Change Data Capture Report",
    "",
    "## Objective",
    "Capture incremental INSERT, UPDATE, and DELETE operations from an operational inventory table, append them to a CDC ledger, and replay them into an analytical table.",
    "",
    "## Execution summary",
    "",
    f"- Events captured: {len(events)}",
    f"- Events applied: {sum(int(e['applied']) for e in events)}",
    f"- INSERT events: {ops.get('INSERT', 0)}",
    f"- UPDATE events: {ops.get('UPDATE', 0)}",
    f"- DELETE events: {ops.get('DELETE', 0)}",
    "",
    "## Validation log",
    "",
]
lines += [f"- {line}" for line in log[1:]]
lines += [
    "",
    "## Interpretation",
    "",
    "CDC synchronizes downstream analytical state by applying only recorded row changes rather than repeatedly copying the full source table. This demo replays captured events in event order and marks each event as applied in the same transaction as the analytical change.",
    "",
    "## Limitations",
    "",
    "This is an educational SQLite simulation using explicit event-capture calls. It is not PostgreSQL WAL-based CDC and does not demonstrate replication-slot recovery or production-grade exactly-once delivery. The supplied PostgreSQL schema is a starting reference for an extension.",
]
(OUT / "cdc_report.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
print("Report generated: output/cdc_report.md")
