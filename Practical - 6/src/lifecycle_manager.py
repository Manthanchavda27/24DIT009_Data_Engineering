import csv, json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT/"config"/"lifecycle_policy.json").read_text(encoding="utf-8"))
DATA, OUT = ROOT/"data", ROOT/"output"
OUT.mkdir(exist_ok=True)
today = date.fromisoformat(policy["as_of_date"])

def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

objects = rows(DATA/"operational_logs.csv")
access = {r["object_key"]: r for r in rows(DATA/"access_manifest.csv")}
audits = rows(DATA/"server_audit.csv")
results, logs = [], [f"Policy: {policy['policy_name']}", f"Evaluation date: {today}", f"Audit records loaded: {len(audits)}", "-"*60]

for obj in objects:
    a = access[obj["object_key"]]
    age = (today-date.fromisoformat(obj["created_date"])).days
    since = (today-date.fromisoformat(a["last_access_date"])).days
    count, retention, size = int(a["accesses_last_30_days"]), int(obj["retention_days"]), float(obj["size_gb"])
    if age >= retention and policy["retention"]["mark_expired_candidates_only"]:
        tier, reason = "EXPIRED_CANDIDATE", f"retention target reached ({age}d >= {retention}d); flagged only"
    elif since <= policy["hot"]["recent_access_days"] or count >= policy["hot"]["minimum_accesses_in_30_days"]:
        tier, reason = "HOT", f"last access {since}d ago; {count} accesses in 30d"
    elif since <= policy["warm"]["recent_access_days"]:
        tier, reason = "WARM", f"last access {since}d ago"
    else:
        tier, reason = "COLD", f"last access {since}d ago; archival candidate"
    rate_key = {"HOT":"hot", "WARM":"warm", "COLD":"cold"}.get(tier)
    rate = policy[rate_key]["illustrative_cost_per_gb_month"] if rate_key else 0.0
    results.append({"object_key":obj["object_key"],"created_date":obj["created_date"],"age_days":age,
                    "last_access_date":a["last_access_date"],"days_since_access":since,
                    "accesses_last_30_days":count,"size_gb":size,"retention_days":retention,
                    "proposed_tier":tier,"illustrative_cost_per_gb_month":rate,"reason":reason})
    logs.append(f"{tier:18} {obj['object_key']} | age={age}d | since_access={since}d | accesses30d={count} | {reason}")

(OUT/"lifecycle_execution.json").write_text(json.dumps({"policy_name":policy["policy_name"],"evaluation_date":str(today),"objects_evaluated":len(results),"results":results}, indent=2), encoding="utf-8")
(OUT/"lifecycle_audit.log").write_text("\n".join(logs)+"\n", encoding="utf-8")
counts = {}
for r in results: counts[r["proposed_tier"]] = counts.get(r["proposed_tier"],0)+1
print(f"Policy evaluated {len(results)} objects.")
for tier, count in sorted(counts.items()): print(f"  {tier}: {count}")
print("Saved output/lifecycle_execution.json and output/lifecycle_audit.log")
