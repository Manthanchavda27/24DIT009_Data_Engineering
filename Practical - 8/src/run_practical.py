import argparse
import json
import time
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"


def generate_data(rows: int) -> pd.DataFrame:
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    csv_path = DATA / "clickstream.csv"
    parquet_path = DATA / "clickstream.parquet"
    partition_dir = DATA / "partitioned"

    if csv_path.exists():
        csv_path.unlink()
    if parquet_path.exists():
        parquet_path.unlink()
    if partition_dir.exists():
        import shutil
        shutil.rmtree(partition_dir)

    df = pd.DataFrame({
        "event_id": range(1, rows + 1),
        "user_id": [f"user_{i % max(1000, rows // 10):07d}" for i in range(rows)],
        "event_type": ["click" if i % 4 else "purchase" if i % 12 == 0 else "view" for i in range(rows)],
        "page": [f"/page/{i % 80}" for i in range(rows)],
        "region": [["west", "east", "north", "south"][i % 4] for i in range(rows)],
        "year": [2025 if i % 5 else 2024 for i in range(rows)],
        "month": [(i % 12) + 1 for i in range(rows)],
        "event_value": [(i % 500) / 10.0 for i in range(rows)],
    })
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)
    df.to_parquet(partition_dir, index=False, partition_cols=["year", "month"])
    return df


def timed_query(con, label, query):
    start = time.perf_counter()
    result = con.execute(query).fetchall()
    elapsed = time.perf_counter() - start
    return {"label": label, "seconds": round(elapsed, 6), "result": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1_000_000)
    args = parser.parse_args()
    if args.rows < 1000:
        raise SystemExit("Use at least 1000 rows for a meaningful demo.")

    print(f"Generating {args.rows:,} clickstream rows...")
    df = generate_data(args.rows)
    csv = (DATA / "clickstream.csv").as_posix()
    parquet = (DATA / "clickstream.parquet").as_posix()
    partitions = (DATA / "partitioned").as_posix()

    con = duckdb.connect()
    # Escape single quotes in paths for SQL string literals.
    csv = csv.replace("'", "''")
    parquet = parquet.replace("'", "''")
    partitions = partitions.replace("'", "''")

    queries = [
        ("CSV baseline: aggregate by region", f"""
            SELECT region, COUNT(*) AS events, ROUND(AVG(event_value), 2) AS avg_value
            FROM read_csv_auto('{csv}')
            WHERE year = 2025 AND month = 3
            GROUP BY region ORDER BY region
        """),
        ("Parquet: same aggregation", f"""
            SELECT region, COUNT(*) AS events, ROUND(AVG(event_value), 2) AS avg_value
            FROM read_parquet('{parquet}')
            WHERE year = 2025 AND month = 3
            GROUP BY region ORDER BY region
        """),
        ("Partitioned Parquet: filtered aggregation", f"""
            SELECT region, COUNT(*) AS events, ROUND(AVG(event_value), 2) AS avg_value
            FROM read_parquet('{partitions}/**/*.parquet', hive_partitioning=true)
            WHERE year = 2025 AND month = 3
            GROUP BY region ORDER BY region
        """),
        ("Nested query baseline", f"""
            SELECT region, total_events, avg_value
            FROM (
                SELECT region, COUNT(*) AS total_events, AVG(event_value) AS avg_value
                FROM read_parquet('{parquet}')
                GROUP BY region
            ) q
            WHERE total_events > 0
            ORDER BY region
        """),
        ("CTE refactor", f"""
            WITH region_summary AS (
                SELECT region, COUNT(*) AS total_events, AVG(event_value) AS avg_value
                FROM read_parquet('{parquet}')
                GROUP BY region
            )
            SELECT region, total_events, avg_value
            FROM region_summary
            WHERE total_events > 0
            ORDER BY region
        """),
    ]

    results = []
    plans = []
    print("\nRunning queries...")
    for label, query in queries:
        item = timed_query(con, label, query)
        results.append({"label": item["label"], "seconds": item["seconds"],
                        "result": item["result"]})
        print(f"- {label}: {item['seconds']:.6f} sec")
        print(f"  Result rows: {len(item['result'])}")
        plans.append(f"\n{'=' * 78}\n{label}\nSQL:\n{query.strip()}\n\nEXPLAIN ANALYZE:\n")
        try:
            plan_rows = con.execute("EXPLAIN ANALYZE " + query).fetchall()
            plans.extend(str(row) + "\n" for row in plan_rows)
        except Exception as exc:
            plans.append(f"Could not collect EXPLAIN ANALYZE: {exc}\n")

    report = {
        "practical": "Practical 8 - Query Processing and Optimization",
        "engine": f"DuckDB {duckdb.__version__}",
        "dataset_rows": len(df),
        "csv_bytes": (DATA / "clickstream.csv").stat().st_size,
        "parquet_bytes": (DATA / "clickstream.parquet").stat().st_size,
        "results": results,
        "notes": [
            "Timings are machine- and cache-dependent.",
            "Parquet is columnar; partitioned Parquet can prune irrelevant partitions.",
            "DuckDB is columnar; this practical does not demonstrate B-tree indexes."
        ],
    }
    (OUT / "benchmark_report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    (OUT / "execution_plans.txt").write_text("".join(plans), encoding="utf-8")

    md = [
        "# Practical 8 — Query Processing and Optimization",
        "",
        f"- Engine: DuckDB {duckdb.__version__}",
        f"- Dataset rows: {len(df):,}",
        f"- CSV size: {report['csv_bytes']:,} bytes",
        f"- Parquet size: {report['parquet_bytes']:,} bytes",
        "",
        "## Benchmark results",
        "",
        "| Query | Runtime (seconds) | Result rows |",
        "|---|---:|---:|",
    ]
    for r in results:
        md.append(f"| {r['label']} | {r['seconds']:.6f} | {len(r['result'])} |")
    md += [
        "",
        "## Interpretation",
        "",
        "- A full table scan reads all relevant input rows; it can become expensive as data grows.",
        "- Columnar Parquet lets analytical engines read only required columns and often compresses data well.",
        "- Hive-style year/month partitioning can skip partitions that do not match filters.",
        "- CTEs improve readability and can help restructure complex queries; they are not guaranteed to be faster than nested subqueries.",
        "- Compare the execution plans in `execution_plans.txt` and avoid claiming a fixed speedup.",
        "",
        "## Deliverables",
        "",
        "- `benchmark_report.json`: timings, result sets, dataset and file sizes.",
        "- `execution_plans.txt`: EXPLAIN ANALYZE output for each query.",
    ]
    (OUT / "practical_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    con.close()
    print("\nDone.")
    print(f"CSV size: {report['csv_bytes']:,} bytes")
    print(f"Parquet size: {report['parquet_bytes']:,} bytes")
    print("Reports: output\\benchmark_report.json, output\\execution_plans.txt, output\\practical_report.md")
    print("Review execution plans and timings before taking screenshots.")


if __name__ == "__main__":
    main()
