import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Connect to MySQL (Update with your credentials)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="meher@2005",
    database="your_db"
)
cursor = db.cursor()

@app.route("/get_clustered_data", methods=["GET"])
def get_clustered_data():
    query = "SELECT transaction_id, transaction_amount FROM transactions WHERE transaction_amount IS NOT NULL"
    df = pd.read_sql(query, db)

    # Apply K-Means clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[["transaction_amount"]])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(X_scaled)

    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
