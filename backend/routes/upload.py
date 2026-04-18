from fastapi import APIRouter, UploadFile, File
import os
from backend.services.advanced_analyzer import analyze_document_advanced
from backend.services.memory import save_analysis

from PIL import Image
import pytesseract
import pdfplumber

import cv2
import numpy as np

router = APIRouter()

UPLOAD_DIR = "backend/uploads"

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -------- Image preprocessing --------
def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        return None

    # grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # noise removal
    gray = cv2.medianBlur(gray, 3)

    # threshold
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    return thresh


@router.post("/upload")
async def upload_file(user_id: str, file: UploadFile = File(...)):

    # -------- FILE FORMAT CHECK --------
    allowed = [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".pdf"]

    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        return {
            "error": "Unsupported format. Please upload PNG, JPG, JPEG, or PDF."
        }

    # -------- CREATE USER FOLDER --------
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, file.filename)

    # -------- SAVE FILE --------
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # -------- TEXT EXTRACTION --------
    text = ""

    try:
        # -------- PDF --------
        if file.filename.lower().endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

        # -------- IMAGE --------
        else:
            processed = preprocess_image(file_path)

            if processed is not None:
                text = pytesseract.image_to_string(processed, lang="eng+hin")
            else:
                text = ""

    except Exception as e:
        text = f"Error reading file: {str(e)}"

    # -------- ANALYSIS --------
    # analysis = analyze_document(text)

    # -------- ADVANCED ANALYSIS --------
    analysis = analyze_document_advanced(file_path)

    # -------- SAVE MEMORY --------
    save_analysis(user_id, analysis)

    return {
        "filename": file.filename,
        "extracted_text": text[:300],  # preview
        "analysis": analysis,
        "message": "File processed successfully"
    }