from backend.services.normalizer import normalize_input
from backend.services.intent_detector import detect_intent, Intent
from backend.services.medical_db import get_symptoms, get_medicines, format_context
from backend.services.page_index import search
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ✅ Fix 1: mutable default argument fix — list ki jagah None
async def process(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    # Layer 1 — Normalize
    norm = await normalize_input(user_message)

    # Layer 2 — Intent
    intent = detect_intent(norm)

    symptoms = norm.get("normalized_symptoms", [])
    meds = norm.get("normalized_medicines", [])

    context = ""

    # Layer 3 — Retrieval
    # ✅ Fix 2: MIXED intent handle kiya
    if intent == Intent.DOCUMENT_QUERY:
        docs = search(norm.get("document_keywords", []))
        context = "\n".join(docs)

    elif intent == Intent.MIXED:
        # Dono — medical DB + PageIndex dono se search
        sym_data = get_symptoms(symptoms)
        med_data = get_medicines(meds)
        docs = search(symptoms + meds)
        context = format_context(sym_data, med_data) + "\n" + "\n".join(docs)

    else:
        # SYMPTOM_CHAT, MEDICINE_QUERY, GENERAL_CHAT
        sym_data = get_symptoms(symptoms)
        med_data = get_medicines(meds)
        context = format_context(sym_data, med_data)

    # Layer 4 — Response
    system_prompt = f"""
You are a helpful medical assistant.
Respond in the same language the user used (Hinglish/Hindi/English).
Be simple, warm, and clear. Never diagnose definitively.
Always recommend a doctor for serious issues.

Context from knowledge base:
{context}
"""

    # ✅ Fix 3: conversation_history ab actually use ho raha hai
    messages = [{"role": "system", "content": system_prompt}]

    # last 6 messages — 3 turns (user + assistant)
    messages.extend(conversation_history[-6:])

    messages.append({"role": "user", "content": user_message})

    res = await client.chat.completions.create(
        model="gpt-4o-mini",
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