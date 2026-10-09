import duckdb
import pandas as pd

from common import OUTPUT_DIR, ensure_output_dir

def run():
    ensure_output_dir()

    etl_db = OUTPUT_DIR / "etl.duckdb"
    elt_db = OUTPUT_DIR / "elt.duckdb"

    if not etl_db.exists() or not elt_db.exists():
        raise FileNotFoundError("Run both etl_pipeline.py and elt_pipeline.py first.")

    con1 = duckdb.connect(str(etl_db), read_only=True)
    con2 = duckdb.connect(str(elt_db), read_only=True)

    etl = con1.execute("""
        SELECT * FROM clean_sales
        ORDER BY transaction_id
    """).df()
    elt = con2.execute("""
        SELECT * FROM clean_sales
        ORDER BY transaction_id
    """).df()

    con1.close()
    con2.close()

    # Normalize dtypes for a deterministic comparison.
    etl["transaction_date"] = pd.to_datetime(etl["transaction_date"])
    elt["transaction_date"] = pd.to_datetime(elt["transaction_date"])
    etl["quantity"] = etl["quantity"].astype("int64")
    elt["quantity"] = elt["quantity"].astype("int64")
    etl["unit_price"] = etl["unit_price"].round(6)
    elt["unit_price"] = elt["unit_price"].round(6)
    etl["total_amount"] = etl["total_amount"].round(6)
    elt["total_amount"] = elt["total_amount"].round(6)

    same_shape = etl.shape == elt.shape
    same_values = etl.equals(elt)

    summary = pd.DataFrame([{
        "etl_rows": len(etl),
        "elt_rows": len(elt),
        "same_shape": same_shape,
        "same_values": same_values,
        "status": "PASS" if same_shape and same_values else "FAIL",
    }])
    summary.to_csv(OUTPUT_DIR / "comparison.csv", index=False)

    print(summary.to_string(index=False))

    if not same_shape or not same_values:
        raise SystemExit("ETL and ELT outputs do not match. Inspect comparison.csv.")

if __name__ == "__main__":
    run()
