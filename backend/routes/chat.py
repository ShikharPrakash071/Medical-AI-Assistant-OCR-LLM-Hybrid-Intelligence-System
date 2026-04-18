from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.llm_service import get_response
from backend.utils.language import detect_language
from backend.services.memory import save_message, get_history

router = APIRouter()

class Query(BaseModel):
    message: str
    user_id: str = "default_user"

@router.post("/chat")
def chat(query: Query):

    lang = detect_language(query.message)

    # save message
    save_message(query.user_id, query.message)

    history = get_history(query.user_id)

    ai_response = get_response(query.message, lang)

    # follow-up based on language
    if lang == "hinglish":
        ai_response += "\n\nKya aapko aur koi symptoms feel ho rahe hain?"
    else:
        ai_response += "\n\nAre you experiencing any other symptoms?"

    # LEVEL 2 trigger
    if len(history) >= 4:
        last_messages = [item["message"] for item in history[-3:]]

        if len(set(last_messages)) == 1:
            ai_response += "\n\nAgar aapko relief nahi mil raha, toh please apni reports ya documents upload karein."

    return {
        "user_input": query.message,
        "response": ai_response,
        "language_detected": lang,
        "history": history
    }