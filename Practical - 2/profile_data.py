import pandas as pd

def profile():

    df = pd.read_csv("data/customers.csv")

    print("\n===== DATA PROFILE =====")

    print("\nRows :", len(df))

    print("Columns :", len(df.columns))

    print("\nColumn Names")

    print(df.columns.tolist())

    print("\nData Types")

    print(df.dtypes)

    print("\nMissing Values")

    print(df.isnull().sum())

    print("\nDuplicate Rows")

    print(df.duplicated().sum())