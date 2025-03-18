import streamlit as st
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pdf2image import convert_from_bytes
import re
import io

# Set page config
st.set_page_config(page_title="BFSI OCR", layout="wide")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "users" not in st.session_state:
    st.session_state.users = {"admin@example.com": "password"}  # Default admin user

# Function to authenticate user
def authenticate(email, password):
    if email in st.session_state.users and st.session_state.users[email] == password:
        st.session_state.authenticated = True
        st.session_state.current_user = email  # Store current user session
        st.success("✅ Login Successful! Redirecting...")
        st.rerun()
    else:
        st.error("❌ Invalid credentials. Please try again.")

# Function to register user
def register_user(email, password):
    if email in st.session_state.users:
        st.error("⚠️ Email already registered. Please login.")
    else:
        st.session_state.users[email] = password
        st.success("✅ Registration successful! You can now login.")

# Logout Function
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.success("✅ Logged out successfully!")
    st.rerun()

# Show login form only if not authenticated
if not st.session_state.authenticated:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        st.title("🔒 Login")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        if st.button("Login"):
            authenticate(email, password)

    elif page == "Register":
        st.title("📝 Register")
        new_email = st.text_input("Email", placeholder="Enter your email")
        new_password = st.text_input("Password", placeholder="Create a password", type="password")
        if st.button("Register"):
            register_user(new_email, new_password)

else:
    # Show menu after login
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Select a Page", ["Home", "Document Processor", "Student Loan Approval", "Logout"], index=0)

    if menu == "Home":
        st.title("🏠 Welcome to BFSI OCR Website")
        st.write(f"Logged in as: {st.session_state.current_user}")

    elif menu == "Document Processor":
        st.title("📄 Document Processor")
        st.write("Upload and process documents here.")

    elif menu == "Student Loan Approval":
        st.title("💰 Student Loan Approval")
        st.write("Apply for a student loan based on AI-based eligibility criteria.")

    elif menu == "Logout":
        logout()

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

        # Bar Chart
        st.subheader("Transaction Bar Chart")
        fig_bar, ax_bar = plt.subplots(figsize=(10, 3))
        df.plot(kind='bar', x='Date', y='Amount', ax=ax_bar, color='royalblue', legend=False)
        ax_bar.set_title("Transaction Bar Chart")
        ax_bar.set_ylabel("Amount")
        ax_bar.set_xlabel("Date")
        st.pyplot(fig_bar)

        # Pie Chart
        st.subheader("Transaction Pie Chart")
        pastel_colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c2f0c2', '#f0e68c']
        fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
        df.groupby('Date')['Amount'].sum().plot(kind='pie', autopct='%1.1f%%', colors=pastel_colors, ax=ax_pie)
        ax_pie.set_ylabel("")
        ax_pie.set_title("Transaction Pie Chart")
        st.pyplot(fig_pie)

        # Line Cha
        st.subheader("Transaction Line Chart")
        fig_line, ax_line = plt.subplots(figsize=(10, 3))
        df.plot(kind='line', x='Date', y='Amount', ax=ax_line, marker='o', linestyle='-', color='navy', legend=False)
        ax_line.set_title("Transaction Line Chart")
        ax_line.set_ylabel("Amount")
        ax_line.set_xlabel("Date")
        st.pyplot(fig_line)

    # Document Processor
    if menu == "Document Processor":
        st.title("Document Processor")
        doc_type = st.selectbox("Select Type", ["--Select--","Supervised", "Unsupervised", "Semi-Supervised"])
        
        sub_type = None
        if doc_type == "Supervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Bank Statement", "Invoice", "Payslip", "Profit & Loss Statement"])
        elif doc_type == "Unsupervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Stock Market"])
        elif doc_type == "Semi-Supervised":
            sub_type = st.selectbox("Select Document Type", ["--Select--","Handwritten Document"])
        
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
                    transaction_text = '\n'.join([f"{t[0]} - {t[1]}: {t[2]}" for t in transactions])
                    st.text_area("Extracted Transactions", transaction_text, height=200)
                    
                    # Show Visualizations
                    st.subheader("Visualizations")
                    visualize_financial_data(transactions)
                else:
                    st.warning("No financial transactions detected.")


    elif menu == "Student Loan Approval":
        
        name = st.text_input("Student Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        marks_10 = st.number_input("10th Grade Score (%)", min_value=0, max_value=100, value=60)
        marks_12 = st.number_input("12th Grade Score (%)", min_value=0, max_value=100, value=60)
        income = st.number_input("Monthly Income", min_value=0, step=100000)
        loan_amount = st.number_input("Loan Amount", min_value=0, step=100000)
        cibil = st.number_input("CIBIL Score", min_value=300, max_value=900, step=10)
        tenure = st.selectbox("Loan Tenure", [1, 3, 5, 7, 10, 15])
        
        banks = [
            {"Bank": "SBI of India", "Min Income": 10000, "CIBIL": 300, "Tenure": [1, 3, 5, 10]},
            {"Bank": "Punjab National Bank", "Min Income": 20000, "CIBIL": 650, "Tenure": [1, 5, 7]},
            {"Bank": "HDFC", "Min Income": 5000, "CIBIL": 550, "Tenure": [1, 3, 5, 10, 15]},
            {"Bank": "Central Bank of India", "Min Income": 30000, "CIBIL": 700, "Tenure": [5, 10]}
        ]
        
        if st.button("Find Banks"):
            available_banks = [
                bank for bank in banks if income >= bank["Min Income"] and cibil >= bank["CIBIL"] and tenure in bank["Tenure"]
            ]
            
            if available_banks:
                st.subheader("Banks Offering Loans")
                for bank in available_banks:
                    st.write(f"**{bank['Bank']}** - Available for tenure: {', '.join(map(str, bank['Tenure']))} years")
            else:
                st.warning("No banks found matching the criteria.")
