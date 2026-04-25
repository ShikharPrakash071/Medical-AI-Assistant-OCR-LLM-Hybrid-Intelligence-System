import json, os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Convert user input into structured JSON.
Return ONLY JSON:
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)

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