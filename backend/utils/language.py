def detect_language(text):
    hindi_words = ["hai", "kya", "kaise", "mujhe", "dard", "sir"]

    for word in hindi_words:
        if word in text.lower():
            return "hinglish"

    return "english"