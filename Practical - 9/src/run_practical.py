from pathlib import Path
import json
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"
DB = DATA / "practical9.duckdb"


def main():
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()

    n = 50000
    df = pd.DataFrame({
        "order_id": [f"ORD{i // 2 + 1:06d}" for i in range(n)],
        "order_date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-02-15", "2025-03-20", "2025-04-05"] * (n // 5)),
        "customer_id": [f"CUST{i % 500 + 1:04d}" for i in range(n)],
        "customer_name": [f"Customer {i % 500 + 1}" for i in range(n)],
        "city": [["Anand", "Vadodara", "Ahmedabad", "Surat", "Rajkot"][i % 5] for i in range(n)],
        "region": [["Central", "Central", "North", "South", "Saurashtra"][i % 5] for i in range(n)],
        "product_id": [f"PROD{i % 100 + 1:03d}" for i in range(n)],
        "product_name": [f"Product {i % 100 + 1}" for i in range(n)],
        "category": [["Electronics", "Grocery", "Clothing", "Home", "Sports"][i % 5] for i in range(n)],
        "category_group": [["Durable", "Consumable", "Apparel", "Household", "Lifestyle"][i % 5] for i in range(n)],
        "quantity": [(i % 5) + 1 for i in range(n)],
        "unit_price": [round(50 + (i % 200) * 1.25, 2) for i in range(n)],
    })
    df["sales_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df.to_csv(DATA / "transactional_sales.csv", index=False)

    con = duckdb.connect(str(DB))
    con.register("sales_df", df)
    con.execute("CREATE TABLE raw_sales AS SELECT * FROM sales_df")
    customers = con.execute("""
        SELECT ROW_NUMBER() OVER (ORDER BY customer_id)::INTEGER AS customer_key,
               customer_id, customer_name, city, region,
               DATE '2025-01-01' AS effective_from,
               DATE '9999-12-31' AS effective_to,
               TRUE AS is_current
        FROM (SELECT DISTINCT customer_id, customer_name, city, region FROM raw_sales)
    """).df()
    products = con.execute("""
        SELECT ROW_NUMBER() OVER (ORDER BY product_id)::INTEGER AS product_key,
               product_id, product_name, category, category_group
        FROM (SELECT DISTINCT product_id, product_name, category, category_group FROM raw_sales)
    """).df()
    dates = con.execute("""
        SELECT ROW_NUMBER() OVER (ORDER BY order_date)::INTEGER AS date_key,
               order_date::DATE AS full_date,
               YEAR(order_date)::INTEGER AS year,
               QUARTER(order_date)::INTEGER AS quarter,
               MONTH(order_date)::INTEGER AS month,
               STRFTIME(order_date, '%B') AS month_name,
               DAY(order_date)::INTEGER AS day_of_month
        FROM (SELECT DISTINCT order_date FROM raw_sales)
    """).df()
    con.register("customers_df", customers)
    con.register("products_df", products)
    con.register("dates_df", dates)
    con.execute("CREATE TABLE dim_customer AS SELECT * FROM customers_df")
    con.execute("CREATE TABLE dim_product AS SELECT * FROM products_df")
    con.execute("CREATE TABLE dim_date AS SELECT * FROM dates_df")
    con.execute("""
        CREATE TABLE fact_sales AS
        SELECT ROW_NUMBER() OVER (ORDER BY r.order_id, r.customer_id, r.product_id)::BIGINT AS sales_key,
               r.order_id, c.customer_key, p.product_key, d.date_key,
               r.quantity, r.unit_price, r.sales_amount
        FROM raw_sales r
        JOIN dim_customer c USING (customer_id)
        JOIN dim_product p USING (product_id)
        JOIN dim_date d ON d.full_date = r.order_date::DATE
    """)
    con.execute("""
        CREATE TABLE dim_category AS
        SELECT ROW_NUMBER() OVER (ORDER BY category)::INTEGER AS category_key,
               category AS category_name, category_group
        FROM (SELECT DISTINCT category, category_group FROM raw_sales)
    """)
    queries = [
        ("Revenue by region", """
            SELECT c.region, ROUND(SUM(f.sales_amount), 2) AS revenue
            FROM fact_sales f JOIN dim_customer c USING (customer_key)
            GROUP BY c.region ORDER BY revenue DESC
        """),
        ("Monthly revenue", """
            SELECT d.year, d.month, d.month_name, ROUND(SUM(f.sales_amount), 2) AS revenue
            FROM fact_sales f JOIN dim_date d USING (date_key)
            GROUP BY d.year, d.month, d.month_name ORDER BY d.year, d.month
        """),
        ("Top 5 products", """
            SELECT p.product_name, ROUND(SUM(f.sales_amount), 2) AS revenue
            FROM fact_sales f JOIN dim_product p USING (product_key)
            GROUP BY p.product_name ORDER BY revenue DESC LIMIT 5
        """),
        ("Snowflake-style category revenue", """
            SELECT cat.category_name, ROUND(SUM(f.sales_amount), 2) AS revenue
            FROM fact_sales f
            JOIN dim_product p USING (product_key)
            JOIN dim_category cat ON cat.category_name = p.category
            GROUP BY cat.category_name ORDER BY revenue DESC
        """),
    ]
    query_out = []
    for label, sql in queries:
        result = con.execute(sql).df()
        query_out.append(f"\\n## {label}\\nSQL:\\n{sql.strip()}\\n\\nResult:\\n{result.to_string(index=False)}\\n")
    tables = ["raw_sales", "dim_customer", "dim_product", "dim_date", "fact_sales", "dim_category"]
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
    (OUT / "table_counts.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    (OUT / "query_results.txt").write_text("\\n".join(query_out), encoding="utf-8")
    (OUT / "schema.sql").write_text((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"), encoding="utf-8")
    report = f"""# Practical 9 — Data Modeling for Analytics

## Dataset
- Source rows: {len(df):,}
- Unique customers: {len(customers):,}
- Unique products: {len(products):,}
- Unique dates: {len(dates):,}

## Table row counts
| Table | Rows |
|---|---:|
""" + "\\n".join(f"| {t} | {counts[t]:,} |" for t in tables) + """

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
"""
    (OUT / "model_report.md").write_text(report, encoding="utf-8")
    print("Practical 9 completed successfully.")
    print(f"Source rows: {len(df):,}")
    print("Table row counts:")
    for table, count in counts.items():
        print(f"  {table}: {count:,}")
    print("\\nGenerated files:")
    print("  data\\transactional_sales.csv")
    print("  output\\table_counts.json")
    print("  output\\query_results.txt")
    print("  output\\schema.sql")
    print("  output\\model_report.md")
    con.close()


if __name__ == "__main__":
    main()
