import pickle
import numpy as np
import sys

# Load trained model
model = pickle.load(open("loan_model.pkl", "rb"))

def predict_loan(income, loan_amount, cibil_score):
    features = np.array([[income, loan_amount, cibil_score]])
    prediction = model.predict(features)
    print("Approved" if prediction == 1 else "Rejected")
    sys.stdout.flush()

if __name__ == "__main__":
    predict_loan(float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]))
