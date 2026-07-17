import sqlite3
import pandas as pd
import os

os.makedirs("database", exist_ok=True)

def store():

    conn = sqlite3.connect("database/ecommerce.db")

    df = pd.read_csv("data/customers.csv")

    df.to_sql("Customers",conn,if_exists="replace",index=False)

    conn.commit()

    conn.close()

    print("SQLite database created.")