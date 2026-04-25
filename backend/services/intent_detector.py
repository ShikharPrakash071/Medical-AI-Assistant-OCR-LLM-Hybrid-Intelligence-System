from enum import Enum


class Intent(str, Enum):
    SYMPTOM_CHAT   = "symptom_chat"
    MEDICINE_QUERY = "medicine_query"
    DOCUMENT_QUERY = "document_query"
    MIXED          = "mixed"
    GENERAL_CHAT   = "general_chat"


def detect_intent(n: dict) -> Intent:
    if n.get("is_document_query"):
        return Intent.DOCUMENT_QUERY

    s = bool(n.get("normalized_symptoms"))
    m = bool(n.get("normalized_medicines"))

    if s and m:
        return Intent.MIXED       # dono hain — hybrid retrieval

    if m:
        return Intent.MEDICINE_QUERY

    if s:
        return Intent.SYMPTOM_CHAT

    return Intent.GENERAL_CHAT