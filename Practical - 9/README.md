# Practical 9 — Data Modeling for Analytics

## Objective
Transform repeated transactional sales data into a Kimball-style star schema: dimension tables hold descriptive attributes, while a central fact table holds numeric measures and foreign keys. Run analytical queries in DuckDB and compare the star schema with a simple snowflake-style hierarchy.

## Windows CMD setup
```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python src\run_practical.py
```

## What the program does
1. Creates a synthetic sales CSV with repeated customer, product, category, and region attributes.
2. Loads it into DuckDB as a raw table.
3. Builds a star schema with `dim_customer`, `dim_product`, `dim_date`, and `fact_sales`.
4. Uses surrogate keys while preserving source business IDs.
5. Includes effective dates and an `is_current` flag to demonstrate the SCD Type 2 design pattern.
6. Runs analytical queries and writes schema SQL, counts, and results to `output/`.
7. Creates a snowflake-style category table for comparison.

## Output files
- `data/transactional_sales.csv`
- `output/schema.sql`
- `output/model_report.md`
- `output/query_results.txt`
- `output/table_counts.json`

## Notes
This is a runnable local DuckDB demonstration using synthetic data. It shows the SCD Type 2 structure, but does not implement a full incremental SCD2 load process.
