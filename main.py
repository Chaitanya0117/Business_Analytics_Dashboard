import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Step 1: Connect to database
conn = sqlite3.connect("business.db")
cursor = conn.cursor()

# Step 2: Load CSV
df = pd.read_csv("orders.csv")

# Step 3: Add Total Column
df['Total'] = df['Quantity'] * df['Price']

# Step 4: Store in SQL
df.to_sql("orders", conn, if_exists="replace", index=False)

print("\n✅ Data Loaded into Database")

# ---------------- SQL ANALYSIS ---------------- #

# 1. Total Revenue
total_revenue = cursor.execute("""
SELECT SUM(Total) FROM orders
""").fetchone()[0]

print("\n💰 Total Revenue:", total_revenue)

# 2. Top Products
top_products = pd.read_sql_query("""
SELECT Product, SUM(Total) as Revenue
FROM orders
GROUP BY Product
ORDER BY Revenue DESC
""", conn)

print("\n🛒 Top Products:\n", top_products)

# 3. Top Customers
top_customers = pd.read_sql_query("""
SELECT Customer, SUM(Total) as Spending
FROM orders
GROUP BY Customer
ORDER BY Spending DESC
""", conn)

print("\n👤 Top Customers:\n", top_customers)

# 4. Monthly Sales
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M')

monthly_sales = pd.read_sql_query("""
SELECT substr(Date,1,7) as Month, SUM(Total) as Revenue
FROM orders
GROUP BY Month
ORDER BY Month
""", conn)

print("\n📈 Monthly Sales:\n", monthly_sales)

# ---------------- VISUALIZATION ---------------- #

# Top Products Chart
plt.figure()
plt.bar(top_products['Product'], top_products['Revenue'])
plt.title("Top Products by Revenue")
plt.xlabel("Product")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Monthly Sales Chart
plt.figure()
plt.plot(monthly_sales['Month'], monthly_sales['Revenue'])
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ---------------- INSIGHTS ---------------- #

print("\n--- BUSINESS INSIGHTS ---")

top_product = top_products.iloc[0]
print(f"🔥 {top_product['Product']} is the highest revenue generating product.")

top_customer = top_customers.iloc[0]
print(f"💎 {top_customer['Customer']} is the top customer.")

if total_revenue > 200000:
    print("📊 Business is performing well with strong revenue.")

# Close DB
conn.close()