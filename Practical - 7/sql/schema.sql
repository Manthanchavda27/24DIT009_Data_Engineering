-- Practical 7: CDC schema reference (SQLite-compatible SQL)
CREATE TABLE IF NOT EXISTS operational_inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cdc_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    product_id INTEGER NOT NULL,
    before_data TEXT,
    after_data TEXT,
    captured_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytical_inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    updated_at TEXT NOT NULL
);
