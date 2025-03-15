import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import random
from datetime import datetime, timedelta

# Generate synthetic data
np.random.seed(42)
categories = ["Groceries", "Entertainment", "Subscriptions", "Dining", "Travel", "Utilities"]
n_samples = 200

def generate_transaction_id(index):
    return f"TXN{1000 + index}"

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

def generate_customer_name(index):
    first_names = ["John", "Jane", "Alice", "Bob", "Emma", "Michael", "Sarah", "David"]
    last_names = ["Doe", "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_timestamp():
    start_date = datetime(2025, 1, 1)
    random_days = timedelta(days=random.randint(0, 60))
    random_time = timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return (start_date + random_days + random_time).strftime("%Y-%m-%d %H:%M:%S")

data = []
for i in range(n_samples):
    transaction = {
        "transaction_id": generate_transaction_id(i),
        "account_number": generate_account_number() if random.random() > 0.05 else "",  # Some missing account numbers
        "customer_name": generate_customer_name(i),
        "transaction_amount": round(random.uniform(10, 1000), 2) if random.random() > 0.05 else None,  # Some missing amounts
        "transaction_type": random.choice(["Debit", "Credit"]),
        "merchant_category": random.choice(categories) if random.random() > 0.1 else None,  # Some missing categories
        "location": random.choice(["New York, USA", "Los Angeles, USA", "Chicago, USA", "Houston, USA", "Miami, USA"]),
        "timestamp": generate_timestamp(),
        "fraud_flag": random.choice([True, False])
    }
    data.append(transaction)

df = pd.DataFrame(data)

# Display first few rows of the synthetic data
print("Synthetic Data Sample:")
print(df.head())

# Feature selection for clustering
X = df[["transaction_amount"]].dropna()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply K-means clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df.loc[X.index, "Cluster"] = kmeans.fit_predict(X_scaled)

# Display first few rows with clusters
print("\nData with Clusters:")
print(df.head())

# Visualization
plt.figure(figsize=(10, 6))
plt.scatter(df.dropna()["transaction_amount"], df.dropna().index, c=df.dropna()["Cluster"], cmap='viridis', alpha=0.6, edgecolors='k')
plt.xlabel("Transaction Amount ($)")
plt.ylabel("Transaction Index")
plt.title("K-means Clustering of Transactions")
plt.colorbar(label="Cluster")
plt.show()
