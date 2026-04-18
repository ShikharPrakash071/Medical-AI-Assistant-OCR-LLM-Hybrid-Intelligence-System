# -------- CONFIG --------
from backend.config import USE_VISION
import backend.config as config   # for runtime update

# -------- ENV + OPENAI --------
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- LIBRARIES --------
import pytesseract
import easyocr
import cv2
import pdfplumber
from rapidfuzz import fuzz
import base64

# init easyocr
reader = easyocr.Reader(['en', 'hi'])


# -------- PREPROCESS --------
def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    return thresh


# -------- OCR 1 (Tesseract) --------
def ocr_tesseract(img):
    if img is None:
        return ""
    return pytesseract.image_to_string(img, lang="eng+hin")


# -------- OCR 2 (EasyOCR) --------
def ocr_easy(path):
    try:
        result = reader.readtext(path, detail=0)
        return " ".join(result)
    except:
        return ""


# -------- OCR 3 (PDF) --------
def extract_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    except:
        pass
    return text


# -------- FUSION --------
def merge_texts(*texts):
    return " ".join([t for t in texts if t])


# -------- FUZZY DETECTION --------
MEDS = ["paracetamol", "ibuprofen", "dextrose", "ors"]

def detect_meds(text):
    found = []
    for med in MEDS:
        if fuzz.partial_ratio(med, text.lower()) > 80:
            found.append(med)
    return found


# -------- VISION AI --------
def vision_analysis(image_path):

    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract disease, medicines, dosage from this prescription"},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img}"}
                ]
            }
        ]
    )

    return response.choices[0].message.content


# -------- SAFE VISION (IMPORTANT) --------
def safe_vision_analysis(file_path):
    try:
        return vision_analysis(file_path)

    except Exception as e:
        error_msg = str(e)

        # 🔴 Auto disable if quota खत्म
        if "quota" in error_msg or "429" in error_msg:
            config.USE_VISION = False
            print("⚠️ Vision disabled due to quota limit")

        print("Vision Error:", error_msg)
        return None


# -------- MAIN PIPELINE --------
def analyze_document_advanced(file_path):

    text = ""

    # -------- PDF --------
    if file_path.endswith(".pdf"):
        text = extract_pdf(file_path)

    # -------- IMAGE --------
    else:
        processed = preprocess_image(file_path)

        t1 = ocr_tesseract(processed)
        t2 = ocr_easy(file_path)

        text = merge_texts(t1, t2)

    meds = detect_meds(text)

    vision_output = None

    # 🔵 Use vision only if enabled
    if USE_VISION:
        vision_output = safe_vision_analysis(file_path)

    # -------- FINAL OUTPUT --------
    if vision_output:
        return {
            "mode": "vision",
            "vision_output": vision_output,
            "fallback_text": text[:300]
        }

    else:
        return {
            "mode": "offline",
            "raw_text": text[:500],
            "meds_detected": meds,
            "note": "Vision disabled or failed"
        }