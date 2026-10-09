# Practical 8 — Query Processing and Optimization

**Goal:** Generate a large clickstream dataset, inspect DuckDB query plans, measure query runtimes, and compare a baseline query with optimizations using Parquet, partition pruning, and query refactoring.

## Requirements
- Python 3.10+
- Windows CMD
- DuckDB and pandas (installed from `requirements.txt`)

## Run on Windows
Open CMD in this folder, then:

```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python src\run_practical.py --rows 1000000
```

For a quicker first test, use `--rows 100000`.

## What it creates
- `data\clickstream.csv` — denormalized clickstream dataset
- `data\clickstream.parquet` — columnar Parquet file
- `data\partitioned\year=2025\month=...` — partitioned Parquet dataset
- `output\benchmark_report.json` — runtimes and row counts
- `output\execution_plans.txt` — DuckDB EXPLAIN / EXPLAIN ANALYZE output
- `output\practical_report.md` — readable summary

## What to demonstrate
1. CSV baseline query scans the full CSV dataset.
2. Parquet query reads columnar data and can avoid reading unused columns.
3. Partition-filtered query can prune irrelevant partitions.
4. Compare a nested query with an equivalent CTE-based query.
5. Review the before/after runtimes and execution plans.

## Important interpretation notes
- Query timings depend on your laptop, disk, OS cache, and dataset size. Do not expect a fixed speedup.
- DuckDB is a columnar analytical engine; this practical demonstrates scan reduction and partition pruning rather than B-tree index creation.
- Parquet and partitioning are useful optimizations for analytical workloads. They do not guarantee every query will be faster.
- For a stronger test, run at least 1,000,000 rows and repeat the run if you want to compare timing stability.

## Screenshots to save
- Successful terminal run and row count
- CSV vs Parquet/partitioned query results and timings
- `output\execution_plans.txt`
- `output\benchmark_report.json`
- `output\practical_report.md`
