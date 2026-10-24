-- Practical 9: Analytics dimensional model
CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR NOT NULL,
    customer_name VARCHAR,
    city VARCHAR,
    region VARCHAR,
    effective_from DATE,
    effective_to DATE,
    is_current BOOLEAN
);

CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    product_name VARCHAR,
    category VARCHAR,
    category_group VARCHAR
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR,
    day_of_month INTEGER
);

CREATE TABLE fact_sales (
    sales_key BIGINT PRIMARY KEY,
    order_id VARCHAR,
    customer_key INTEGER,
    product_key INTEGER,
    date_key INTEGER,
    quantity INTEGER,
    unit_price DOUBLE,
    sales_amount DOUBLE
);

-- Snowflake extension: separate category hierarchy.
CREATE TABLE dim_category (
    category_key INTEGER PRIMARY KEY,
    category_name VARCHAR,
    category_group VARCHAR
);
