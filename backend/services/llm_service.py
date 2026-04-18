def get_response(user_input, lang):

    text = user_input.lower()

    symptoms = []

    # multi symptom detection
    if "headache" in text or "sir" in text:
        symptoms.append("headache")

    if "fever" in text:
        symptoms.append("fever")

    if "stomach" in text or "pet" in text:
        symptoms.append("stomach pain")

    if "dizziness" in text:
        symptoms.append("dizziness")

    if "weakness" in text:
        symptoms.append("weakness")

    # severity detection
    serious_keywords = ["severe", "unbearable", "chest pain", "breathing"]
    is_serious = any(word in text for word in serious_keywords)

    symptom_text = ", ".join(symptoms) if symptoms else "your symptoms"

    # Hinglish response
    if lang == "hinglish":

        response = f"Aapko {symptom_text} ho raha hai.\n\n"

        # follow-up questions
        response += "Kya ye symptoms recently start huye hain?\n"
        response += "Kya aapko weakness ya nausea bhi feel ho raha hai?\n"

        # advice
        response += "\nAbhi ke liye:\n- Rest karein\n- Paani zyada piyen\n"

        if is_serious:
            response += "\n⚠️ Ye symptoms serious ho sakte hain, please turant doctor se consult karein."
        else:
            response += "\nAgar symptoms continue rahe, toh doctor se consult karein."

        return response

    # English response
    else:

        response = f"You are experiencing {symptom_text}.\n\n"

        response += "Did these symptoms start recently?\n"
        response += "Are you also feeling weakness or nausea?\n"

        response += "\nFor now:\n- Take rest\n- Stay hydrated\n"

        if is_serious:
            response += "\n⚠️ These symptoms may be serious, please consult a doctor immediately."
        else:
            response += "\nIf symptoms persist, consult a doctor."

        return response