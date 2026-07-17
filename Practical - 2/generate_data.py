from faker import Faker
import pandas as pd
import random
import json
import os

fake = Faker()

os.makedirs("data", exist_ok=True)

customers = []

for i in range(1,101):
    customers.append({
        "customer_id": i,
        "name": fake.name(),
        "email": fake.email() if random.random() > 0.05 else "",
        "phone": fake.phone_number() if random.random() > 0.05 else "",
        "city": fake.city()
    })

df = pd.DataFrame(customers)
df.to_csv("data/customers.csv", index=False)

transactions = []

for i in range(1,51):
    transactions.append({
        "transaction_id": i,
        "customer_id": random.randint(1,100),
        "product":{
            "id": random.randint(1000,1010),
            "name": fake.word()
        },
        "amount": random.randint(500,5000),
        "status": random.choice(["Success","Pending","Failed"])
    })

with open("data/api_transactions.json","w") as f:
    json.dump(transactions,f,indent=4)

with open("data/config.txt","w") as f:
    f.write("DATABASE=SQLite\n")
    f.write("API_URL=https://example.com/api\n")
    f.write("MAX_RECORDS=100\n")
    f.write("LOG_LEVEL=INFO\n")

print("Sample data generated successfully.")