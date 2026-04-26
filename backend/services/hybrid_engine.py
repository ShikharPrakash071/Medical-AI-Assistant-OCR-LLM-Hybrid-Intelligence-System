from backend.services.normalizer import normalize_input
from backend.services.intent_detector import detect_intent, Intent
from backend.services.medical_db import get_symptoms, get_medicines, format_context
from backend.services.page_index import search
from groq import AsyncGroq
import os

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


async def process(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    # Layer 1 - Normalize
    norm = await normalize_input(user_message)

    # Layer 2 - Intent
    intent = detect_intent(norm)

    symptoms = norm.get("normalized_symptoms", [])
    meds = norm.get("normalized_medicines", [])

    context = ""

    # Layer 3 - Retrieval
    if intent == Intent.DOCUMENT_QUERY:
        docs = search(norm.get("document_keywords", []))
        context = "\n".join(docs)

    elif intent == Intent.MIXED:
        sym_data = get_symptoms(symptoms)
        med_data = get_medicines(meds)
        docs = search(symptoms + meds)
        context = format_context(sym_data, med_data) + "\n" + "\n".join(docs)

    else:
        # SYMPTOM_CHAT, MEDICINE_QUERY, GENERAL_CHAT
        sym_data = get_symptoms(symptoms)
        med_data = get_medicines(meds)
        context = format_context(sym_data, med_data)

    # Layer 4 - Response
    system_prompt = f"""
You are a warm, helpful medical assistant for Indian users.
Reply in the EXACT same language the user used - Hinglish, Hindi, or English.

FOLLOW THIS STRUCTURE IN EVERY RESPONSE:

1. ACKNOWLEDGE - User ke symptoms ko warmly acknowledge karo (1-2 lines)

2. HOME REMEDIES - Knowledge base se home remedies batao (2-3 points)

3. MEDICINES - Yeh section MANDATORY hai, kabhi skip mat karo:
   - Generic medicine ka naam batao
   - Indian brand name batao (jaise Crocin, Dolo 650, Brufen)
   - Short dosage batao
   - - Sabhi medicines list karne ke BAAD, sirf EK BAAR likho: "doctor se confirm zaroor karein"

4. DOCTOR KAB MILEIN - Knowledge base se when_to_see_doctor info batao

5. FOLLOW-UP - Ek follow-up question pucho

STRICT RULES:
- Medicines HAMESHA suggest karo - yeh bot ka main purpose hai
- Diagnose KABHI mat karo
- Knowledge base mein jo data hai wahi use karo
- User ki language mein hi jawab do - English user ko English mein, Hinglish user ko Hinglish mein

Knowledge Base:
{context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})

    res = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.4,
        max_tokens=800
    )

    return {
        "reply": res.choices[0].message.content,
        "intent": intent,
        "intent_label": str(intent),
        "sources": ["db" if context else "none"],
        "debug": norm
    }