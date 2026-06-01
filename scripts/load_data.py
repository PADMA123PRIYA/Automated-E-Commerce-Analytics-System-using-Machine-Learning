import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your mysql password",  # 🔴 change this
    database="ecommerce"
)

cursor = conn.cursor()

# Read CSV
df = pd.read_csv("../data/orders.csv")

# Insert data
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO orders (order_id, product, city, price, date)
        VALUES (%s, %s, %s, %s, %s)
    """, tuple(row))

# Save
conn.commit()

print("✅ Data inserted successfully!")