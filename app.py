import streamlit as st
import auth
import yfinance as yf
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pdf2image import convert_from_bytes
import re
import io
import bcrypt
import jwt
import datetime
import math

# Set page config
st.set_page_config(page_title="BFSI OCR & LOAN ELIGIBILITY", layout="wide")

# Secret key for JWT
token_secret = "your_secret_key"

# Initialize session state for authentication
if "token" not in st.session_state:
    st.session_state.token = None
if "users" not in st.session_state:
    st.session_state.users = {
        "admin@example.com": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }  # Default admin user with hashed password
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# Function to authenticate user
def authenticate(email, password):
    if email in st.session_state.users:
        stored_hash = st.session_state.users[email]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            payload = {"email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
            token = jwt.encode(payload, token_secret, algorithm='HS256')
            st.session_state.token = token
            st.session_state.current_page = "home"
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")
    else:
        st.error("❌ Invalid credentials. Please try again.")

# Function to register user
def register_user(email, password):
    if email in st.session_state.users:
        st.error("⚠️ Email already registered. Please login.")
    else:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        st.session_state.users[email] = hashed_password
        st.success("✅ Registration successful! You can now login.")
        st.session_state.current_page = "login"
        st.rerun()

# Logout Function
def logout():
    st.session_state.token = None
    st.session_state.current_page = "login"
    st.rerun()

# EMI Calculation Function
def calculate_emi(principal, annual_rate, tenure_years):
    monthly_rate = annual_rate / (12 * 100)  # Convert annual rate to monthly
    tenure_months = tenure_years * 12  # Convert years to months

    if monthly_rate == 0:
        emi = principal / tenure_months  # Simple division if interest rate is 0%
    else:
        emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / (math.pow(1 + monthly_rate, tenure_months) - 1)

    return round(emi, 2), round(emi * tenure_months, 2), round((emi * tenure_months) - principal, 2)


# Function to verify JWT token
def verify_token():
    if st.session_state.token:
        try:
            jwt.decode(st.session_state.token, token_secret, algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            st.session_state.token = None
            st.warning("⚠️ Session expired. Please login again.")
        except jwt.InvalidTokenError:
            st.session_state.token = None
            st.warning("⚠️ Invalid session. Please login again.")
    return False

# OCR Function
def extract_text(image):
    return pytesseract.image_to_string(image)

# Process text to extract financial transactions
def process_financial_text(text):
    transactions = []
    for line in text.split('\n'):
        match = re.search(r'(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d,.]+)', line)
        if match:
            date, description, amount = match.groups()
            transactions.append((date, description, float(amount.replace(',', ''))))
    return transactions


# Visualization function
def visualize_financial_data(transactions):
    if not transactions:
        st.warning("No valid transactions found.")
        return
    
    df = pd.DataFrame(transactions, columns=['Date', 'Description', 'Amount'])
    # Save CSV file
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name="transactions.csv", mime='text/csv')

    
    # Bar Chart
    st.subheader("Transaction Bar Chart")
    fig_bar, ax_bar = plt.subplots(figsize=(10, 3))
    df.plot(kind='bar', x='Date', y='Amount', ax=ax_bar, color='royalblue', legend=False)
    ax_bar.set_title("Transaction Bar Chart", color='white')
    ax_bar.set_ylabel("Amount", color='white')
    ax_bar.set_xlabel("Date", color='white')
    fig_bar.patch.set_alpha(0)  # Set background transparent
    ax_bar.set_facecolor("black")  # Dark background
    ax_bar.tick_params(axis='x', colors='white')
    ax_bar.tick_params(axis='y', colors='white')
    st.pyplot(fig_bar)

    # Pie Chart
    st.subheader("Transaction Pie Chart")
    fig, ax = plt.subplots(figsize=(8, 6))  # Increase figure size

# Create pie chart with better label positioning
    wedges, texts, autotexts = ax.pie(
        df["Amount"], 
        labels=df["Description"], 
        autopct='%1.1f%%', 
        colors=plt.cm.Pastel1.colors,
        textprops={'fontsize': 10},  # Reduce font size
        startangle=140,  # Rotate for better readability
        pctdistance=0.75  # Move percentage labels inside
    )

    # Adjust text colors
    for text in texts + autotexts:
        text.set_color("white")

    # Move legend outside
    ax.legend(wedges, df["Description"], title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))

    # Remove background
    fig_bar.patch.set_alpha(0)  # Set background transparent
    ax_bar.set_facecolor("black")  # Dark background

    st.pyplot(fig)


    # Line Chart
    st.subheader("Transaction Line Chart")
    fig_line, ax_line = plt.subplots(figsize=(10, 3))
    df.plot(kind='line', x='Date', y='Amount', ax=ax_line, marker='o', linestyle='-', color='navy', legend=False)
    ax_line.set_title("Transaction Line Chart", color='white')
    ax_line.set_ylabel("Amount", color='white')
    ax_line.set_xlabel("Date", color='white')
    fig_line.patch.set_alpha(0)  # Set background transparent
    ax_line.set_facecolor("black")  # Dark background
    ax_line.tick_params(axis='x', colors='white')
    ax_line.tick_params(axis='y', colors='white')
    st.pyplot(fig_line)

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data

# Page Routing
if not verify_token():
    if st.session_state.current_page == "login":
        st.title("🔒 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                authenticate(email, password)
        with col2:
            if st.button("Register"):
                st.session_state.current_page = "register"
                st.rerun()
    elif st.session_state.current_page == "register":
        st.title("📝 Register")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Register"):
                register_user(new_email, new_password)
        with col2:
            if st.button("Back to Login"):
                st.session_state.current_page = "login"
                st.rerun()
else:
    # Tab Navigation
    tab1, tab2, tab3, tab4 = st.tabs(["Home", "Document Processor", "Loan Eligibility", "Logout"])
    
    with tab1:
        st.title("🏠 Welcome to Smart BFSI OCR & Student Loan Eligibility")
    
    with tab2:
        st.title("📄 Document Processor")
        doc_type = st.selectbox("Select Type", ["--Select--","Supervised", "Unsupervised", "Semi-Supervised"])
        
        sub_type = None
        if doc_type == "Supervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Bank Statement", "Invoice", "Payslip", "Profit & Loss Statement"])
        elif doc_type == "Unsupervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Stock Market"])
        elif doc_type == "Semi-Supervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Handwritten Document"])
        
        
        if doc_type in ["Supervised", "Semi-Supervised"]:
            uploaded_file = st.file_uploader("Upload Document", type=["png", "jpg", "jpeg", "pdf"])
            if uploaded_file and sub_type:
                image = None
                if uploaded_file.name.endswith(".pdf"):
                    pdf_bytes = uploaded_file.read()
                    images = convert_from_bytes(pdf_bytes)
                    image = images[0] if images else None
                else:
                    image = Image.open(io.BytesIO(uploaded_file.read()))
                
                if image:
                    st.image(image, caption="Uploaded Document", use_column_width=True)
                    text = extract_text(image)
                    st.text_area("Extracted Full Text", text, height=300)

                    transactions = process_financial_text(text)
                    if transactions:
                        st.subheader("Extracted Transactions")
                        df = pd.DataFrame(transactions, columns=['Date', 'Description', 'Amount'])
                        st.dataframe(df)
                        
                        # Show Visualizations
                        st.subheader("Visualizations")
                        visualize_financial_data(transactions)
                    else:
                        st.warning("No financial transactions detected.")

        elif sub_type and sub_type == "Stock Market":
            st.subheader("📈 Stock Market Analysis")
            stock1 = st.text_input("Enter First Stock Ticker (e.g., AAPL)")
            stock2 = st.text_input("Enter Second Stock Ticker (e.g., MSFT)")
            start_date = st.date_input("Select Start Date")
            end_date = st.date_input("Select End Date")
            
            if st.button("Compare Stocks"):
                if stock1 and stock2:
                    df1 = fetch_stock_data(stock1, start_date, end_date)
                    df2 = fetch_stock_data(stock2, start_date, end_date)
                    
                    if df1 is not None and df2 is not None:
                        st.subheader("Closing Price Comparison")
                        fig, ax = plt.subplots()
                        ax.plot(df1.index, df1['Close'], label=stock1)
                        ax.plot(df2.index, df2['Close'], label=stock2)
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Closing Price")
                        ax.legend()
                        st.pyplot(fig)
                        
                        st.subheader("Trading Volume Comparison")
                        fig, ax = plt.subplots()
                        ax.bar(df1.index, df1['Volume'], alpha=0.5, label=stock1)
                        ax.bar(df2.index, df2['Volume'], alpha=0.5, label=stock2)
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Volume")
                        ax.legend()
                        st.pyplot(fig)
                else:
                    st.error("Error fetching stock data. Please check tickers and date range.")

    
    with tab3:
        st.title("💰 Student Loan Eligibility")
        name = st.text_input("Student Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        marks_10 = st.number_input("10th Grade Score (%)", min_value=0, max_value=100, value=60)
        marks_12 = st.number_input("12th Grade Score (%)", min_value=0, max_value=100, value=60)
        income = st.number_input("Monthly Income", min_value=0, step=100000)
        loan_amount = st.number_input("Loan Amount", min_value=0, step=100000)
        cibil = st.slider("CIBIL Score", min_value=300, max_value=900, step=10)
        tenure = st.selectbox("Loan Tenure", [1, 3, 5, 7, 10, 15])
        
        banks = [
            {"Bank": "SBI of India", "Min Income": 10000, "CIBIL": 300, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.5, "Processing Time": 7, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Quick approval", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 10000, "CIBIL": 330, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.4, "Reviews": ["Fast processing", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 350, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 370, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 400, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 450, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates", "Good customer service"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 500, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 550, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 600, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 650, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 700, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 750, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 800, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 850, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "SBI of India", "Min Income": 12000, "CIBIL": 900, "Tenure": [1, 2, 3, 4, 5], "Interest Rate": 10.0, "Processing Time": 5, "Loan Amount Min": 10000, "Loan Amount Max": 500000, "Rating": 4.5, "Reviews": ["Fast processing", "Low interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 300, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.5, "Processing Time": 5, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.0, "Reviews": ["Fast processing", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 330, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.3, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 350, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 370, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 400, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 450, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 500, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 550, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 600, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 650, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 700, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 750, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 800, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 850, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "HDFC Bank", "Min Income": 12000, "CIBIL": 900, "Tenure": [1, 2, 3, 4, 5, 6], "Interest Rate": 11.0, "Processing Time": 6, "Loan Amount Min": 15000, "Loan Amount Max": 750000, "Rating": 4.2, "Reviews": ["Good service", "High interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 300, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.5, "Processing Time": 6, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.1, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 330, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 100000 , "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 350, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 370, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 400, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 450, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 500, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 550, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 600, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 650, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 700, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 750, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 800, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 850, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "ICICI Bank", "Min Income": 12000, "CIBIL": 900, "Tenure": [1, 2, 3, 4, 5, 6, 7], "Interest Rate": 12.0, "Processing Time": 7, "Loan Amount Min": 20000, "Loan Amount Max": 1000000, "Rating": 4.0, "Reviews": ["Average service", "Moderate interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 300, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.5, "Processing Time": 7, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.9, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 330, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 350, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 370, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 400, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 450, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 500, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 550, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 600, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 650, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},
            {"Bank": "Axis Bank", "Min Income": 12000, "CIBIL": 700, "Tenure": [1, 2, 3, 4, 5, 6, 7, 8], "Interest Rate": 13.0, "Processing Time": 8, "Loan Amount Min": 25000, "Loan Amount Max": 1250000, "Rating": 3.8, "Reviews": ["Slow processing", "High interest rates"]},

        ]
           
        
        if st.button("Find Banks"):
            available_banks = [
                bank for bank in banks if income >= bank["Min Income"] and cibil >= bank["CIBIL"] and tenure in bank["Tenure"]
            ]
            
            if available_banks:
                st.subheader("Banks Offering Loans")
                for bank in available_banks:
                    with st.expander(f"💰 **{bank['Bank']}** (⭐ {bank['Rating']}/5)"):
                        # Loan details
                        st.write(f"📅 **Available Tenure:** {', '.join(map(str, bank['Tenure']))} years")
                        st.write(f"💵 **Loan Amount:** ₹{bank['Loan Amount Min']} - ₹{bank['Loan Amount Max']}")
                        st.write(f"💲 **Interest Rate:** {bank['Interest Rate']}%")
                        st.write(f"⏳ **Processing Time:** {bank['Processing Time']} days")


                        # User Reviews
                        st.write("💬 **User Reviews:**")
                        for review in bank['Reviews']:
                            st.write(f"📝 {review}")

            else:
                st.warning("No banks found matching the criteria.")
            
        st.divider()
        st.title("📊 EMI Calculator")

        # User Inputs
        loan_amount = st.number_input("Enter Loan Amount (₹)", min_value=10000, max_value=5000000, value=100000, step=5000, key="loan_amt")
        interest_rate = st.number_input("Enter Annual Interest Rate (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.1, key="int_rate")
        loan_tenure = st.number_input("Enter Loan Tenure (Years)", min_value=1, max_value=30, value=5, step=1, key="loan_tenure")

        # Calculate EMI on button click
        if st.button("📌 Calculate EMI"):
            emi, total_payment, total_interest = calculate_emi(loan_amount, interest_rate, loan_tenure)

            # Display Results
            st.subheader("💰 EMI Details")
            st.write(f"🟢 **Monthly EMI:** ₹{emi}")
            st.write(f"📈 **Total Interest Payable:** ₹{total_interest}")
            st.write(f"💵 **Total Payment (Principal + Interest):** ₹{total_payment}")

            # Visual Representation
            st.progress(min(int((loan_amount / total_payment) * 100), 100))

            # Pie Chart for Principal vs Interest (Reduced Size)
            fig, ax = plt.subplots(figsize=(4, 4))  # Adjust figure size
            fig.patch.set_alpha(0)  # Make figure background transparent
            ax.patch.set_alpha(0)  # Make axes background transparent

            labels = ["Principal", "Interest"]
            sizes = [loan_amount, total_interest]

            # Transparent Blue Shades (RGBA Format)
            colors = [(0.1, 0.4, 0.8, 0.5), (0.3, 0.6, 0.9, 0.5)]  

            # Plot Pie Chart
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct="%1.1f%%", colors=colors, 
                startangle=90, wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'alpha': 0.7}, 
                pctdistance=0.85, radius=0.6  # Further reduced pie size
            )

            # Improve text visibility
            for text in texts:
                text.set_color("white")  # Label color
            for autotext in autotexts:
                autotext.set_color("black")  # Percentage color
                autotext.set_fontsize(9)  # Adjust font size

            # Title Adjustments
            ax.set_title("Loan Breakdown (Principal vs. Interest)", fontsize=10, color='blue')

            # Ensure Circular Pie
            ax.axis("equal")

            # Display in Streamlit without auto-expanding
            st.pyplot(fig, use_container_width=False)


    
    with tab4:
        if st.button("Logout"):
            logout()
