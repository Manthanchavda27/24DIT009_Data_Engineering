import argparse, json, time
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "unpartitioned" / "metrics.parquet"
PART_ROOT = ROOT / "data" / "partitioned"
OUT = ROOT / "output" / "benchmark.json"

def run_query(con, sql):
    t = time.perf_counter()
    rows = con.execute(sql).fetchone()
    return rows, time.perf_counter() - t

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2025)
    p.add_argument("--month", type=int, default=3)
    p.add_argument("--region", choices=["west","north","south","east"], default="west")
    a = p.parse_args()
    if not BASELINE.exists() or not PART_ROOT.exists():
        raise FileNotFoundError("Run prepare_storage.py first.")
    con = duckdb.connect()
    where = f"year={a.year} AND month={a.month} AND region='{a.region}'"
    sql = f"""SELECT COUNT(*), ROUND(AVG(cpu_percent),2), ROUND(AVG(memory_percent),2)
              FROM read_parquet('{BASELINE.as_posix()}') WHERE {where}"""
    full, full_s = run_query(con, sql)
    target = PART_ROOT / f"year={a.year}" / f"month={a.month}" / f"region={a.region}"
    matches = sorted(target.glob("*.parquet")) if target.exists() else []
    if matches:
        file_list = "[" + ",".join("'" + f.as_posix() + "'" for f in matches) + "]"
        psql = f"""SELECT COUNT(*), ROUND(AVG(cpu_percent),2), ROUND(AVG(memory_percent),2)
                   FROM read_parquet({file_list})"""
        part, part_s = run_query(con, psql)
    else:
        part, part_s = (0, None, None), 0.0
    con.close()
    result = {
        "filter": {"year":a.year, "month":a.month, "region":a.region},
        "full_file_scan": {"seconds":round(full_s,6), "rows":full[0], "avg_cpu":full[1], "avg_memory":full[2]},
        "partition_scan": {"seconds":round(part_s,6), "rows":part[0], "avg_cpu":part[1], "avg_memory":part[2],
                           "matching_files":[str(x.relative_to(ROOT)) for x in matches]},
        "validation": {"same_rows":full[0] == part[0], "same_aggregates":full[1:] == part[1:],
                       "status":"PASS" if full == part else "FAIL"}
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Distributed storage benchmark completed.")
    print(f"Filter: year={a.year}, month={a.month:02d}, region={a.region}")
    print(f"Full-file query:   {full_s:.6f}s | rows={full[0]}")
    print(f"Partition query:   {part_s:.6f}s | rows={part[0]}")
    print(f"Matching partition files: {len(matches)}")
    print(f"Validation: {result['validation']['status']}")
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
