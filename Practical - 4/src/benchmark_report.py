import json
from pathlib import Path

from common import OUTPUT_DIR, ensure_output_dir

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def run():
    ensure_output_dir()

    etl = load(OUTPUT_DIR / "etl_lineage.json")
    elt = load(OUTPUT_DIR / "elt_lineage.json")
    comparison = load_comparison()

    report = f"""# Practical 4 — ETL vs ELT Benchmark Report

## Objective
Implement two integration pipelines over identical retail transaction data:
- **ETL:** transform in Python/Pandas memory before loading into DuckDB.
- **ELT:** load raw data into DuckDB staging and transform using DuckDB SQL.

## Dataset
- Input rows: **{etl["input_rows"]:,}**
- ETL output rows: **{etl["output_rows"]:,}**
- ELT output rows: **{elt["output_rows"]:,}**

## Performance

| Metric | ETL | ELT |
|---|---:|---:|
| Extract / raw-load | {etl["timings_seconds"]["extract"]:.6f}s | {elt["timings_seconds"]["extract_and_load_raw"]:.6f}s |
| Transform | {etl["timings_seconds"]["transform"]:.6f}s | {elt["timings_seconds"]["transform"]:.6f}s |
| Load / export | {etl["timings_seconds"]["load"]:.6f}s | {elt["timings_seconds"]["export"]:.6f}s |
| Total | {etl["timings_seconds"]["total"]:.6f}s | {elt["timings_seconds"]["total"]:.6f}s |

## Data Lineage

### ETL
`CSV → Pandas extraction → Pandas transformations → DuckDB clean_sales`

Transformation compute happens in the application process.

### ELT
`CSV → DuckDB raw_sales staging → DuckDB SQL transformations → DuckDB clean_sales`

Raw data is preserved in a staging table before transformation.

## Output Validation
- ETL rows: **{comparison["etl_rows"]:,}**
- ELT rows: **{comparison["elt_rows"]:,}**
- Same shape: **{comparison["same_shape"]}**
- Same values: **{comparison["same_values"]}**
- Validation status: **{comparison["status"]}**

## Interpretation

ETL is attractive when transformation logic belongs close to the application or when the target system has limited transformation capability. It also allows Python/Pandas libraries to be used directly.

ELT is attractive when the target analytical engine has strong SQL processing capabilities. Raw data can be landed first, transformations can be rerun from the staging layer, and transformation logic can remain closer to the analytical storage system.

For this local experiment, the timing numbers are machine-dependent and should be discussed as an experimental observation rather than a universal rule.

## Maintenance and Recovery

**ETL:** A transformation bug requires rerunning the application-side transformation. If only the cleaned output was retained, recovery can require rereading the original source.

**ELT:** Keeping `raw_sales` in staging gives a clear recovery point. SQL transformations can be modified and rerun without regenerating the source file.

## Conclusion

The practical demonstrates the architectural difference between transforming data before loading and loading raw data before transforming. The better choice depends on infrastructure, data volume, transformation complexity, governance, lineage, and where scalable compute is available.
"""
    (OUTPUT_DIR / "final_report.md").write_text(report, encoding="utf-8")
    print("Created output/final_report.md")

def load_comparison():
    import csv
    with (OUTPUT_DIR / "comparison.csv").open(encoding="utf-8", newline="") as f:
        row = next(csv.DictReader(f))
    return {
        "etl_rows": int(row["etl_rows"]),
        "elt_rows": int(row["elt_rows"]),
        "same_shape": row["same_shape"] == "True",
        "same_values": row["same_values"] == "True",
        "status": row["status"],
    }

if __name__ == "__main__":
    run()
