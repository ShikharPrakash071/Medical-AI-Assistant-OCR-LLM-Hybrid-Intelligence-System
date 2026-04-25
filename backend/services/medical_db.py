import json
from pathlib import Path
from difflib import get_close_matches

# ✅ Fix: Path(__file__) use kiya — server kahan se bhi run ho, file milegi
_path = Path(__file__).parent.parent / "data" / "medical_db.json"

with open(_path) as f:
    DB = json.load(f)


def fuzzy(term, keys):
    return get_close_matches(term, keys, n=1, cutoff=0.6)


def get_symptoms(symptoms):
    res = {}
    keys = DB["symptoms"].keys()
    for s in symptoms:
        if s in keys:
            res[s] = DB["symptoms"][s]
        else:
            m = fuzzy(s, keys)
            if m:
                res[s] = DB["symptoms"][m[0]]
    return res


def get_medicines(meds):
    res = {}
    keys = DB["medicines"].keys()
    for m in meds:
        if m in keys:
            res[m] = DB["medicines"][m]
        else:
            f = fuzzy(m, keys)
            if f:
                res[m] = DB["medicines"][f[0]]
    return res


def format_context(sym, med):
    out = []
    for k, v in sym.items():
        out.append(f"{k}: {v.get('description')}")
    for k, v in med.items():
        out.append(f"{k}: used for {v.get('uses')}")
    return "\n".join(out)