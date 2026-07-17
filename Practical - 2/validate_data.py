import pandas as pd
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

def validate():

    df = pd.read_csv("data/customers.csv")

    issues = []

    for index,row in df.iterrows():

        problem=[]

        if pd.isna(row["customer_id"]):
            problem.append("Missing ID")

        if pd.isna(row["name"]):
            problem.append("Missing Name")

        if pd.isna(row["email"]) or row["email"]=="":
            problem.append("Missing Email")

        if pd.isna(row["phone"]) or row["phone"]=="":
            problem.append("Missing Phone")

        issues.append(",".join(problem))

    df["Issues"]=issues

    df.to_csv("output/validation_report.csv",index=False)

    with open("logs/quality_log.txt","a") as f:

        f.write(f"\n{datetime.now()}\n")
        f.write("Validation Executed\n")
        f.write(f"Rows Processed : {len(df)}\n")
        f.write(f"Rows With Issues : {(df['Issues']!='').sum()}\n")
        f.write("-------------------------\n")

    print("Validation completed.")