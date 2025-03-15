# BFSI OCR Project - Loan Approval and Document Processing System

## Overview
The BFSI OCR Project is a web-based application designed to process documents for the BFSI (Banking, Financial Services, and Insurance) industry. The system performs real-time OCR-based text extraction from uploaded documents, visualizes extracted data through various charts, and provides AI-based loan approval predictions. This project includes two primary features:
1. **Document Processor**: OCR-based text extraction from different document types.
2. **Student Loan Approval**: AI-powered loan eligibility prediction for students.

The system also includes robust user authentication and data security.

## Features
- **OCR Document Processing**:
  - Supervised, Unsupervised, and Semi-Supervised document types.
  - File formats supported: PDF, PNG, JPG, etc.
  - Visualizations based on extracted data (Bar, Pie, and Line charts).
  
- **Student Loan Approval**:
  - AI model for loan approval prediction.
  - Features like student information, CIBIL score, income, and loan amount for evaluation.

- **User Authentication**:
  - Secure user login and registration system.

- **Real-Time Data Processing**:
  - Real-time extraction of data from uploaded documents.
  - Dynamic label generation for visualizations based on document content.

## Tech Stack
- **Frontend**:
  - HTML
  - CSS
  - JavaScript

- **Backend**:
  - Python (for AI model and OCR processing)

- **Database**:
  - MySQL

- **OCR Technology**:
  - Python-based OCR libraries (e.g., Tesseract)

- **Cloud Deployment**:
  - AWS, Azure, or GCP (for scalability)

- **Visualization Libraries**:
  - Matplotlib
  - Seaborn

## Setup and Installation

### Prerequisites
1. **Python** 3.7 or higher
2. **MySQL** Database
3. **Tesseract OCR** (Install from [Tesseract's official site](https://github.com/tesseract-ocr/tesseract))
4. **Libraries**:
   - Install Python libraries by running:
   ```bash
   pip install -r requirements.txt
   ```

5. **MySQL Database**:
   - Set up a MySQL database and configure the connection in the `server.py` file.
   - Import the `database.sql` schema to create necessary tables.

### Running the Application
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd BFSI-OCR-Project
   ```

2. Start the Python server (with Flask or a simpler HTTP server if Flask isn't used):
   ```bash
   python server.py
   ```

3. Open the application in your browser:
   ```bash
   http://localhost:5000
   ```

## Usage

### Document Processor:
- Go to the **Document Processor** page.
- Choose the OCR type (Supervised, Unsupervised, Semi-Supervised).
- Select the document type (Bank Statement, Invoice, etc.).
- Upload the document (PDF, PNG, JPG).
- The OCR will extract text, and visualizations like Bar, Pie, or Line charts will be displayed based on the extracted data.

### Student Loan Approval:
- Go to the **Student Loan Approval** page.
- Fill in the form with student information, monthly income, loan amount, and CIBIL score.
- Submit the form to see AI-based loan approval predictions.

## Future Enhancements
- Multi-language support for OCR.
- Enhance AI model with additional features for more accurate loan predictions.
- Add more document types for OCR-based processing.
- Integration with payment gateways for actual loan processing.

## License
This project is licensed under the MIT License.
