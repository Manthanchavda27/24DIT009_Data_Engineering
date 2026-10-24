# Practical 9 — Data Modeling for Analytics

## Dataset
- Source rows: 50,000
- Unique customers: 500
- Unique products: 100
- Unique dates: 5

## Table row counts
| Table | Rows |
|---|---:|
| raw_sales | 50,000 |\n| dim_customer | 500 |\n| dim_product | 100 |\n| dim_date | 5 |\n| fact_sales | 50,000 |\n| dim_category | 5 |

## Model design
- **Fact table:** `fact_sales` stores measures and dimension keys.
- **Dimension tables:** customer, product, and date descriptions support filtering and grouping.
- **Surrogate keys:** warehouse-generated integer keys decouple the model from source business IDs.
- **SCD Type 2 design pattern:** `dim_customer` includes effective dates and `is_current`. This demo creates one current version per customer; a production SCD2 process would add a new version when tracked attributes change.
- **Snowflake extension:** `dim_category` separates category details from product data. It may reduce repeated attributes but adds a join.

## 3NF versus star schema
A normalized 3NF operational model minimizes repeated data and supports consistent transactional updates. A star schema centralizes measures in a fact table and descriptive attributes in dimensions, making common analytical queries simpler.

## Outputs
- `query_results.txt`: analytical SQL and results.
- `table_counts.json`: table counts.
- `schema.sql`: DDL example for star and snowflake-style structures.

This is a local DuckDB demonstration with synthetic data, not a production ingestion pipeline.
