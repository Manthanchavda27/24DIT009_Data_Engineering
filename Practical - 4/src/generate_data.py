import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "retail_sales.csv"

PRODUCTS = [
    ("Laptop", "Electronics"),
    ("Mouse", "Electronics"),
    ("Keyboard", "Electronics"),
    ("Monitor", "Electronics"),
    ("Headphones", "Electronics"),
    ("Office Chair", "Furniture"),
    ("Desk", "Furniture"),
    ("Notebook", "Stationery"),
    ("Pen", "Stationery"),
    ("Backpack", "Accessories"),
]

STORE_CODES = [
    (" ST001 ", "Ahmedabad"),
    ("OLD01", "Ahmedabad"),
    (" ST002", "Vadodara"),
    ("OLD02 ", "Vadodara"),
    ("ST003 ", "Surat"),
    ("OLD03", "Surat"),
    (" ST004", "Rajkot"),
    ("OLD04 ", "Rajkot"),
    ("ST005 ", "Anand"),
    ("OLD05", "Anand"),
]

BASE_PRICES = {
    "Laptop": 55000,
    "Mouse": 900,
    "Keyboard": 1500,
    "Monitor": 12000,
    "Headphones": 2500,
    "Office Chair": 8500,
    "Desk": 11000,
    "Notebook": 120,
    "Pen": 30,
    "Backpack": 1800,
}

def make_row(i: int, start: datetime) -> dict:
    product, category = random.choice(PRODUCTS)
    store_code, _ = random.choice(STORE_CODES)
    quantity = random.randint(1, 8)
    price = BASE_PRICES[product] * random.uniform(0.90, 1.10)
    dt = start + timedelta(minutes=random.randint(0, 365 * 24 * 60))

    # Intentionally introduce whitespace and numeric strings.
    product_value = f" {product} " if i % 5 == 0 else product
    category_value = f" {category}" if i % 7 == 0 else category
    quantity_value = f" {quantity} " if i % 6 == 0 else str(quantity)
    price_value = f" {price:.2f} " if i % 4 == 0 else f"{price:.2f}"

    return {
        "transaction_id": f"TXN{i:07d}",
        "transaction_date": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "store_code": store_code,
        "product": product_value,
        "category": category_value,
        "quantity": quantity_value,
        "unit_price": price_value,
        "customer_id": f"CUST{random.randint(1, 15000):05d}",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100000)
    args = parser.parse_args()

    if args.rows <= 0:
        raise ValueError("--rows must be greater than 0")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    random.seed(42)
    start = datetime(2025, 1, 1)

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "transaction_id",
                "transaction_date",
                "store_code",
                "product",
                "category",
                "quantity",
                "unit_price",
                "customer_id",
            ],
        )
        writer.writeheader()
        for i in range(1, args.rows + 1):
            writer.writerow(make_row(i, start))

    print(f"Generated {args.rows:,} rows")
    print(f"File: {OUT}")

if __name__ == "__main__":
    main()
