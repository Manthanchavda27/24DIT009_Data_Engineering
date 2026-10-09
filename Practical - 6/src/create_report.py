import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT/"config"/"lifecycle_policy.json").read_text(encoding="utf-8"))
result = json.loads((ROOT/"output"/"lifecycle_execution.json").read_text(encoding="utf-8"))
rows = result["results"]
counts = {}
for r in rows: counts[r["proposed_tier"]] = counts.get(r["proposed_tier"],0)+1
baseline = sum(r["size_gb"]*policy["hot"]["illustrative_cost_per_gb_month"] for r in rows)
estimated = sum(r["size_gb"]*r["illustrative_cost_per_gb_month"] for r in rows)
savings = baseline-estimated
pct = savings/baseline*100 if baseline else 0
lines = ["# Practical 6 — Storage Lifecycle Management Report","",
         f"- Evaluation date: {result['evaluation_date']}",f"- Policy: {result['policy_name']}",
         f"- Objects evaluated: {result['objects_evaluated']}","","## Tier distribution","","| Tier | Objects |","|---|---:|"]
for tier,count in sorted(counts.items()): lines.append(f"| {tier} | {count} |")
lines += ["","## Illustrative monthly storage-cost comparison","",
          f"- All-Hot baseline: ${baseline:.4f}/month",f"- Policy-assigned estimate: ${estimated:.4f}/month",
          f"- Estimated difference: ${savings:.4f}/month ({pct:.1f}%)","",
          "> Illustrative rates only, not vendor pricing. Expired candidates are flagged but not deleted. Tiering is simulated; objects are not physically moved.","",
          "## Interpretation","","Recently accessed or frequently accessed objects remain Hot; moderately inactive objects are Warm; older inactive objects are Cold candidates. Objects past their retention age are flagged for review.","",
          "## Generated files","","- `output/lifecycle_execution.json` — per-object decisions.","- `output/lifecycle_audit.log` — execution log.","- `output/lifecycle_report.md` — this report."]
( ROOT/"output"/"lifecycle_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("Report generated: output/lifecycle_report.md")
print(f"Illustrative estimated difference: ${savings:.4f}/month ({pct:.1f}%).")
