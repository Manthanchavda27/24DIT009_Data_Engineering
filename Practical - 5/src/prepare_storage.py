import argparse, random, shutil
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
UNPARTITIONED = DATA / "unpartitioned"
PARTITIONED = DATA / "partitioned"
REGIONS = ["west", "north", "south", "east"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100000)
    args = parser.parse_args()
    if args.rows <= 0:
        raise ValueError("--rows must be greater than zero")
    random.seed(42)
    start = datetime(2023, 1, 1)
    rows = []
    for i in range(args.rows):
        ts = start + timedelta(minutes=random.randint(0, 3 * 365 * 24 * 60))
        rows.append({
            "event_id": f"EVT{i+1:08d}", "event_time": ts,
            "year": ts.year, "month": ts.month, "region": random.choice(REGIONS),
            "cpu_percent": round(random.uniform(1, 99), 2),
            "memory_percent": round(random.uniform(5, 98), 2),
            "requests_per_minute": random.randint(0, 5000)
        })
    df = pd.DataFrame(rows)
    DATA.mkdir(exist_ok=True)
    for folder in [UNPARTITIONED, PARTITIONED]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
    df.to_csv(DATA / "generated_metrics.csv", index=False)
    df.to_parquet(UNPARTITIONED / "metrics.parquet", index=False)
    df.to_parquet(PARTITIONED, index=False, partition_cols=["year", "month", "region"])
    print(f"Generated {len(df):,} metric records.")
    print(f"CSV: {DATA / 'generated_metrics.csv'}")
    print(f"Unpartitioned Parquet: {UNPARTITIONED / 'metrics.parquet'}")
    print(f"Partitioned Parquet root: {PARTITIONED}")
    print("Partition format: year=YYYY/month=MM/region=REGION/")

if __name__ == "__main__":
    main()
