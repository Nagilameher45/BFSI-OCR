import pytesseract
import cv2
import sys

def extract_text(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    print(text)  # This will be read by Node.js
    sys.stdout.flush()
