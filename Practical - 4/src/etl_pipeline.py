import time
import json
from pathlib import Path

import duckdb
import pandas as pd

from common import RAW_FILE, OUTPUT_DIR, ensure_output_dir, store_name, clean_store_code, now_utc

DB_FILE = OUTPUT_DIR / "etl.duckdb"
RESULT_FILE = OUTPUT_DIR / "etl_clean_sales.csv"

def run():
    ensure_output_dir()
    start_all = time.perf_counter()

    # EXTRACT
    t0 = time.perf_counter()
    df = pd.read_csv(RAW_FILE, dtype=str)
    extract_seconds = time.perf_counter() - t0

    # TRANSFORM IN APPLICATION MEMORY
    t1 = time.perf_counter()
    text_cols = ["transaction_id", "product", "category", "customer_id"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    df["store_code"] = df["store_code"].map(clean_store_code)
    df["store_name"] = df["store_code"].map(store_name)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["total_amount"] = df["quantity"].astype(float) * df["unit_price"]

    required = [
        "transaction_id", "transaction_date", "store_code", "store_name",
        "product", "category", "quantity", "unit_price", "total_amount",
        "customer_id"
    ]
    df = df[required].dropna(subset=["transaction_id", "transaction_date", "quantity", "unit_price"])
    transform_seconds = time.perf_counter() - t1

    # LOAD
    t2 = time.perf_counter()
    if DB_FILE.exists():
        DB_FILE.unlink()

    con = duckdb.connect(str(DB_FILE))
    con.register("clean_df", df)
    con.execute("""
        CREATE TABLE clean_sales AS
        SELECT * FROM clean_df
    """)
    con.execute(f"COPY clean_sales TO '{RESULT_FILE.as_posix()}' (HEADER, DELIMITER ',')")
    con.close()
    load_seconds = time.perf_counter() - t2

    total_seconds = time.perf_counter() - start_all

    lineage = {
        "pipeline": "ETL",
        "source": str(RAW_FILE),
        "extract_method": "pandas.read_csv",
        "transform_location": "Python/Pandas application memory",
        "load_target": str(DB_FILE),
        "output_table": "clean_sales",
        "input_rows": int(len(pd.read_csv(RAW_FILE))),
        "output_rows": int(len(df)),
        "timings_seconds": {
            "extract": round(extract_seconds, 6),
            "transform": round(transform_seconds, 6),
            "load": round(load_seconds, 6),
            "total": round(total_seconds, 6),
        },
        "completed_at_utc": now_utc(),
    }
    (OUTPUT_DIR / "etl_lineage.json").write_text(json.dumps(lineage, indent=2), encoding="utf-8")

    print("ETL pipeline completed.")
    print(f"Rows loaded: {len(df):,}")
    print(f"Extract:   {extract_seconds:.4f}s")
    print(f"Transform: {transform_seconds:.4f}s")
    print(f"Load:      {load_seconds:.4f}s")
    print(f"Total:     {total_seconds:.4f}s")

if __name__ == "__main__":
    run()
