import json, os
from groq import AsyncGroq
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a medical language normalizer.
Convert user input (Hindi/Hinglish/English) into structured JSON.

IMPORTANT:
- normalized_symptoms → ALWAYS translate to English 
  (bukhar = fever, sir dard = headache, khansi = cough, pet dard = stomach pain)
- normalized_medicines → ALWAYS translate to English generic name
- language_detected → hinglish / hindi / english
- raw_query_english → full message translated to English
- is_document_query → true only if asking about uploaded file or report
- document_keywords → English keywords if is_document_query is true

Return ONLY valid JSON:
{
  "normalized_symptoms": [],
  "normalized_medicines": [],
  "language_detected": "",
  "raw_query_english": "",
  "is_document_query": false,
  "document_keywords": []
}
"""

async def normalize_input(user_message: str):
    try:
        res = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        content = res.choices[0].message.content

        # Empty response check — JSON crash nahi hoga
        if not content or content.strip() == "":
            print("[Normalizer] Empty response from OpenAI")
            raise ValueError("Empty response from OpenAI")

        return json.loads(content)

    except Exception as e:
        print(f"[Normalizer Error] {e}")
        return {
            "normalized_symptoms": [],
            "normalized_medicines": [],
            "language_detected": "unknown",
            "raw_query_english": user_message,
            "is_document_query": False,
            "document_keywords": []
        }