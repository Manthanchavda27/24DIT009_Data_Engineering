import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
def main():
    path = OUT / "benchmark.json"
    if not path.exists():
        raise FileNotFoundError("Run benchmark_queries.py first.")
    d = json.loads(path.read_text(encoding="utf-8"))
    f, p, v, filt = d["full_file_scan"], d["partition_scan"], d["validation"], d["filter"]
    report = f"""# Practical 5 — Distributed Storage Systems

## Aim
Organize analytical data using Hive-style partitioning, optionally store partition objects in MinIO, and compare full-file and partition-targeted query performance.

## Technologies
Python, Pandas, Parquet/PyArrow, DuckDB, Boto3, Docker and MinIO.

## Partition design
`year=YYYY/month=MM/region=REGION/part-0.parquet`

The baseline dataset is stored at `data/unpartitioned/metrics.parquet`. Partitioned files are stored under `data/partitioned/`.

## Query filter
- Year: {filt["year"]}
- Month: {filt["month"]:02d}
- Region: {filt["region"]}

## Benchmark results

| Metric | Full-file query | Partition-targeted query |
|---|---:|---:|
| Execution time (seconds) | {f["seconds"]:.6f} | {p["seconds"]:.6f} |
| Matching rows | {f["rows"]} | {p["rows"]} |
| Average CPU (%) | {f["avg_cpu"]} | {p["avg_cpu"]} |
| Average memory (%) | {f["avg_memory"]} | {p["avg_memory"]} |

## Validation
- Same row count: {v["same_rows"]}
- Same aggregates: {v["same_aggregates"]}
- Status: **{v["status"]}**

## Interpretation
Hive-style partition keys help analytical engines target a subset of data when filters align with the partition columns. The actual speed difference depends on dataset size, file sizes, caching, and hardware; local benchmark timings are experimental observations, not universal guarantees.

MinIO is an S3-compatible object store. Partition values in object keys create meaningful prefixes that help clients locate data by year, month, and region.

## Conclusion
This experiment demonstrates partitioned data organization, partition-key-based query isolation, and a benchmark comparing a full-file query with a partition-targeted query.
"""
    (OUT / "practical_report.md").write_text(report, encoding="utf-8")
    print(f"Created report: {OUT / 'practical_report.md'}")

if __name__ == "__main__":
    main()
