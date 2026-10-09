import json
import time

import duckdb

from common import RAW_FILE, OUTPUT_DIR, ensure_output_dir, now_utc

DB_FILE = OUTPUT_DIR / "elt.duckdb"
RESULT_FILE = OUTPUT_DIR / "elt_clean_sales.csv"

def run():
    ensure_output_dir()
    start_all = time.perf_counter()

    if DB_FILE.exists():
        DB_FILE.unlink()

    con = duckdb.connect(str(DB_FILE))

    # EXTRACT + LOAD RAW DATA DIRECTLY INTO DATABASE STAGING.
    t0 = time.perf_counter()
    con.execute(f"""
        CREATE TABLE raw_sales AS
        SELECT *
        FROM read_csv_auto(
            '{RAW_FILE.as_posix()}',
            header=true,
            all_varchar=true
        )
    """)
    extract_load_seconds = time.perf_counter() - t0

    # TRANSFORM INSIDE THE TARGET DATABASE ENGINE.
    t1 = time.perf_counter()
    con.execute("""
        CREATE TABLE clean_sales AS
        SELECT
            trim(transaction_id) AS transaction_id,
            try_cast(trim(transaction_date) AS TIMESTAMP) AS transaction_date,
            upper(trim(store_code)) AS store_code,
            CASE upper(trim(store_code))
                WHEN 'ST001' THEN 'AHMEDABAD'
                WHEN 'OLD01' THEN 'AHMEDABAD'
                WHEN 'ST002' THEN 'VADODARA'
                WHEN 'OLD02' THEN 'VADODARA'
                WHEN 'ST003' THEN 'SURAT'
                WHEN 'OLD03' THEN 'SURAT'
                WHEN 'ST004' THEN 'RAJKOT'
                WHEN 'OLD04' THEN 'RAJKOT'
                WHEN 'ST005' THEN 'ANAND'
                WHEN 'OLD05' THEN 'ANAND'
                ELSE 'UNKNOWN'
            END AS store_name,
            trim(product) AS product,
            trim(category) AS category,
            try_cast(trim(quantity) AS INTEGER) AS quantity,
            try_cast(trim(unit_price) AS DOUBLE) AS unit_price,
            try_cast(trim(quantity) AS DOUBLE)
                * try_cast(trim(unit_price) AS DOUBLE) AS total_amount,
            trim(customer_id) AS customer_id
        FROM raw_sales
        WHERE try_cast(trim(transaction_date) AS TIMESTAMP) IS NOT NULL
          AND try_cast(trim(quantity) AS INTEGER) IS NOT NULL
          AND try_cast(trim(unit_price) AS DOUBLE) IS NOT NULL
    """)
    transform_seconds = time.perf_counter() - t1

    t2 = time.perf_counter()
    con.execute(f"COPY clean_sales TO '{RESULT_FILE.as_posix()}' (HEADER, DELIMITER ',')")
    output_rows = con.execute("SELECT COUNT(*) FROM clean_sales").fetchone()[0]
    input_rows = con.execute("SELECT COUNT(*) FROM raw_sales").fetchone()[0]
    con.close()
    load_seconds = time.perf_counter() - t2

    total_seconds = time.perf_counter() - start_all

    lineage = {
        "pipeline": "ELT",
        "source": str(RAW_FILE),
        "extract_load_method": "DuckDB read_csv_auto into raw_sales staging table",
        "transform_location": "DuckDB SQL engine",
        "load_target": str(DB_FILE),
        "staging_table": "raw_sales",
        "output_table": "clean_sales",
        "input_rows": int(input_rows),
        "output_rows": int(output_rows),
        "timings_seconds": {
            "extract_and_load_raw": round(extract_load_seconds, 6),
            "transform": round(transform_seconds, 6),
            "export": round(load_seconds, 6),
            "total": round(total_seconds, 6),
        },
        "completed_at_utc": now_utc(),
    }
    (OUTPUT_DIR / "elt_lineage.json").write_text(json.dumps(lineage, indent=2), encoding="utf-8")

    print("ELT pipeline completed.")
    print(f"Raw rows:  {input_rows:,}")
    print(f"Clean rows:{output_rows:,}")
    print(f"Raw load:  {extract_load_seconds:.4f}s")
    print(f"Transform: {transform_seconds:.4f}s")
    print(f"Export:    {load_seconds:.4f}s")
    print(f"Total:     {total_seconds:.4f}s")

if __name__ == "__main__":
    run()
