import pandas as pd
import mysql.connector
import schedule
import time
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# -------------------------------
# 🔹 STEP 1: TRAIN MODEL (RUN ONCE)
# -------------------------------

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your mysql password",
    database="ecommerce"
)

df = pd.read_sql("SELECT * FROM orders", conn)

# Convert date
df['date'] = pd.to_datetime(df['date'])

# 🚨 ANOMALY DETECTION
mean_price = df['price'].mean()
std_price = df['price'].std()

upper_limit = mean_price + 2 * std_price
lower_limit = mean_price - 2 * std_price

anomalies = df[(df['price'] > upper_limit) | (df['price'] < lower_limit)]

print("\n🚨 Anomalies Detected:")
print(anomalies[['product', 'city', 'price']])

# 📈 SALES TREND
sales_trend = df.groupby('date')['price'].sum().reset_index()

print("\n📈 Sales Trend:")
print(sales_trend.tail())

# 🔤 Encoding (SAVE mapping before encoding)
product_mapping = df['product'].astype('category')
city_mapping = df['city'].astype('category')

df['product'] = product_mapping.cat.codes
df['city'] = city_mapping.cat.codes

# 🎯 Features
X = df[['product', 'city']]
y = df['price']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = LinearRegression()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

print("✅ Model trained & saved!")

# Accuracy
y_pred = model.predict(X_test)
score = r2_score(y_test, y_pred)

print("📊 Model Accuracy (R2 Score):", score)

conn.close()

# -------------------------------
# 🔁 STEP 2: AUTOMATED PIPELINE
# -------------------------------

def run_pipeline():
    print("\n🚀 Running pipeline...")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your mysql password",
        database="ecommerce"
    )

    df = pd.read_sql("SELECT * FROM orders", conn)

    # 🚨 ANOMALY DETECTION
    mean_price = df['price'].mean()
    std_price = df['price'].std()

    upper_limit = mean_price + 2 * std_price
    lower_limit = mean_price - 2 * std_price

    anomalies = df[(df['price'] > upper_limit) | (df['price'] < lower_limit)]

    print("🚨 Anomalies:")
    print(anomalies[['product', 'city', 'price']])

    # 📈 SALES TREND
    df['date'] = pd.to_datetime(df['date'])
    sales_trend = df.groupby('date')['price'].sum().reset_index()

    print("📈 Latest Sales Trend:")
    print(sales_trend.tail())

    # 🔤 Encoding
    product_mapping = df['product'].astype('category')
    city_mapping = df['city'].astype('category')

    df['product'] = product_mapping.cat.codes
    df['city'] = city_mapping.cat.codes

    # 🎯 Features
    X = df[['product', 'city']]

    # Load model
    model = joblib.load("model.pkl")

    # 🎲 Pick random row (REAL data)
    sample_row = df.sample(1)

    product_name = product_mapping.cat.categories[sample_row['product'].values[0]]
    city_name = city_mapping.cat.categories[sample_row['city'].values[0]]

    sample_input = sample_row[['product', 'city']]

    prediction = model.predict(sample_input)

    print("💰 Predicted Price:", prediction[0])

    # 🚨 ALERT SYSTEM
    if prediction[0] < 26000:
        alert_msg = "Low Price"
        print("⚠️ ALERT: Price is too LOW!")

    elif prediction[0] > 25000:
        alert_msg = "High Price"
        print("⚠️ ALERT: Price is too HIGH!")

    else:
        alert_msg = "Normal"

    # 💾 Store in MySQL
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (product, city, predicted_price, prediction_time, alert)
        VALUES (%s, %s, %s, NOW(), %s)
        """,
        (str(product_name), str(city_name), float(prediction[0]), alert_msg)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("✅ Stored in DB!")

# -------------------------------
# ⏰ AUTOMATION
# -------------------------------

schedule.every(10).seconds.do(run_pipeline)

print("⏳ Waiting to run...")

while True:
    schedule.run_pending()
    time.sleep(1)