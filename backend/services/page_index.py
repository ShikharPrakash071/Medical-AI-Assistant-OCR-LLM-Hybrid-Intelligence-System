import json, re, math
from collections import defaultdict

# In-memory index — har document ek entry
# { doc_id: { "text": "...", "freq": { "word": count } } }
index = {}


def tokenize(t: str) -> list:
    """Lowercase + sirf words nikalo"""
    return re.findall(r"\w+", t.lower())


def add(doc_id: str, text: str):
    """
    Document ko index mein daalo.
    Upload ke waqt call hota hai.
    """
    words = tokenize(text)
    freq = defaultdict(int)
    for w in words:
        freq[w] += 1

    index[doc_id] = {
        "text": text,
        "freq": dict(freq)
    }


def search(keywords: list, top_k: int = 3) -> list:
    """
    Keywords se relevant documents dhundho.
    TF scoring — vector/embedding ki zaroorat nahi.
    Normalizer pehle English mein convert kar chuka hota hai.
    """
    q = tokenize(" ".join(keywords))
    scores = []

    for doc_id, data in index.items():
        score = sum(data["freq"].get(w, 0) for w in q)
        if score > 0:
            scores.append((score, data["text"]))

    scores.sort(reverse=True)
    return [text for _, text in scores[:top_k]]