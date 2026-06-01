import pandas as pd
import random
from datetime import datetime, timedelta

# Step 1: Sample data
products = ["Laptop", "Phone", "Tablet", "Headphones"]
cities = ["Chennai", "Mumbai", "Delhi", "Bangalore"]

data = []

# Step 2: Generate 1000 orders
for i in range(1000):
    order = {
        "order_id": i,
        "product": random.choice(products),
        "city": random.choice(cities),
        "price": random.randint(1000, 50000),
        "date": datetime.now() - timedelta(days=random.randint(0, 30))
    }
    data.append(order)

# Step 3: Convert to table
df = pd.DataFrame(data)

# Step 4: Save file
df.to_csv("../data/orders.csv", index=False)

print("✅ Data generated successfully!")