def analyze_document(text):

    text = text.lower()

    result = {
        "disease": None,
        "medicines": []
    }

    if "paracetamol" in text:
        result["medicines"].append("paracetamol")

    if "ibuprofen" in text:
        result["medicines"].append("ibuprofen")

    if "fever" in text:
        result["disease"] = "fever"

    if "headache" in text:
        result["disease"] = "headache"

    return result