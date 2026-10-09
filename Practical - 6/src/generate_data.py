import csv, random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
TODAY = date(2026, 10, 9)
random.seed(42)

profiles = [
    ("app-logs-hot-001", 2, 1, 35, 365, 0.4),
    ("api-events-hot-002", 5, 3, 52, 365, 0.8),
    ("metrics-warm-003", 20, 12, 4, 365, 1.5),
    ("audit-warm-004", 45, 18, 2, 730, 0.7),
    ("archive-cold-005", 150, 120, 0, 1095, 4.2),
    ("legacy-cold-006", 300, 240, 0, 1095, 2.1),
    ("rarely-read-007", 90, 60, 1, 365, 0.9),
    ("frequent-old-008", 200, 2, 25, 730, 1.8),
    ("retention-expired-009", 500, 410, 0, 365, 0.3),
    ("new-upload-010", 0, 0, 0, 365, 0.2),
]

def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

objects, accesses, audits = [], [], []
for name, age, since_access, count, retention, size in profiles:
    key = f"logs/{name}.json"
    objects.append({"object_key": key, "created_date": (TODAY-timedelta(days=age)).isoformat(),
                    "size_gb": size, "retention_days": retention})
    accesses.append({"object_key": key, "last_access_date": (TODAY-timedelta(days=since_access)).isoformat(),
                     "accesses_last_30_days": count})
    audits.append({"timestamp": (TODAY-timedelta(days=min(age,30))).isoformat()+"T12:00:00",
                   "object_key": key, "action": "READ" if count else "WRITE",
                   "actor": "demo-service", "result": "SUCCESS"})

write_csv(DATA/"operational_logs.csv", ["object_key","created_date","size_gb","retention_days"], objects)
write_csv(DATA/"access_manifest.csv", ["object_key","last_access_date","accesses_last_30_days"], accesses)
write_csv(DATA/"server_audit.csv", ["timestamp","object_key","action","actor","result"], audits)
print(f"Generated {len(objects)} sample objects plus access and audit records in {DATA}")
