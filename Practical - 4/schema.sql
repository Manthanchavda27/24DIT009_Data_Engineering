-- DuckDB schema used by Practical 4.
-- The ETL and ELT Python scripts also create these tables automatically.

CREATE TABLE IF NOT EXISTS clean_sales (
    transaction_id VARCHAR,
    transaction_date TIMESTAMP,
    store_code VARCHAR,
    store_name VARCHAR,
    product VARCHAR,
    category VARCHAR,
    quantity INTEGER,
    unit_price DOUBLE,
    total_amount DOUBLE,
    customer_id VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_sales (
    transaction_id VARCHAR,
    transaction_date VARCHAR,
    store_code VARCHAR,
    product VARCHAR,
    category VARCHAR,
    quantity VARCHAR,
    unit_price VARCHAR,
    customer_id VARCHAR
);
