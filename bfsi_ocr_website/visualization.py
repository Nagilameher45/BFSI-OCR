import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Simulated extracted data from OCR (Replace with actual extracted data)
ocr_data = {
    "Months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "Total Transactions": [100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320],
    "Aggregated Invoice Values": [10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000, 30000, 32000]
}

# Convert to DataFrame
df = pd.DataFrame(ocr_data)

# 🔹 Create a Bar Chart for Total Transactions
plt.figure(figsize=(8, 5))
sns.barplot(x=df["Months"], y=df["Total Transactions"], palette="Blues_d")
plt.title("Total Transactions Per Month", fontsize=14)
plt.xlabel("Month")
plt.ylabel("Total Transactions")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# 🔹 Create a Line Chart for Aggregated Invoice Values
plt.figure(figsize=(8, 5))
sns.lineplot(x=df["Months"], y=df["Aggregated Invoice Values"], marker="o", color="red")
plt.title("Aggregated Invoice Values Over Time", fontsize=14)
plt.xlabel("Month")
plt.ylabel("Invoice Value ($)")
plt.grid(axis="both", linestyle="--", alpha=0.7)
plt.show()

# 🔹 Create a Pie Chart for Total Transactions
plt.figure(figsize=(6, 6))
plt.pie(df["Total Transactions"], labels=df["Months"], autopct="%1.1f%%", colors=sns.color_palette("Blues", len(df)))
plt.title("Total Transactions Distribution")
plt.show()
