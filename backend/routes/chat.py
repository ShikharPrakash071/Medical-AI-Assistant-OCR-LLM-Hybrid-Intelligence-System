from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.services.hybrid_engine import process
from backend.services.memory import save_message, get_history
from backend.utils.language import detect_language

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    history: list = Field(default_factory=list)


@router.post("/chat")
async def chat(req: ChatRequest):

    # ── Memory ───────────────────────────────────────────────
    save_message(req.user_id, req.message)
    history = get_history(req.user_id)

    # ── Language detect ───────────────
    lang = detect_language(req.message)

    # ── Hybrid Engine — main brain ────────────────────────────
    result = await process(
        user_message=req.message,
        conversation_history=req.history
    )

    reply = result["reply"]

    # ── Follow-up question ──────────────
    if lang == "hinglish":
        reply += "\n\nKya aapko aur koi symptoms feel ho rahe hain?"
    else:
        reply += "\n\nAre you experiencing any other symptoms?"

    # ── Level 2 trigger ─────────────────
    if len(history) >= 4:
        last_messages = [item for item in history[-3:]]
        if len(set(last_messages)) == 1:
            reply += "\n\nAgar aapko relief nahi mil raha, toh please apni reports ya documents upload karein."

    return {
        "user_input": req.message,
        "response": reply,
        "language_detected": lang,
        "intent": result["intent"],
        "intent_label": result["intent_label"],
        "sources": result["sources"],
        "debug": result["debug"],
        "history": history
    }