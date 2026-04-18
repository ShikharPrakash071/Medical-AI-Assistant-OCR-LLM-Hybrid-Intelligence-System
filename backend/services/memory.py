user_memory = {}

# -------- SAVE MESSAGE --------
def save_message(user_id, message):
    if user_id not in user_memory:
        user_memory[user_id] = {
            "messages": [],
            "stage": 1,
            "answers": {},
            "analysis": {}
        }

    user_memory[user_id]["messages"].append(message)


# -------- GET HISTORY --------
def get_history(user_id):
    if user_id in user_memory:
        return user_memory[user_id]["messages"]
    return []


# -------- GET FULL USER DATA --------
def get_user_data(user_id):
    if user_id not in user_memory:
        user_memory[user_id] = {
            "messages": [],
            "stage": 1,
            "answers": {},
            "analysis": {}
        }

    return user_memory[user_id]


# -------- UPDATE STAGE --------
def update_stage(user_id, stage):
    if user_id in user_memory:
        user_memory[user_id]["stage"] = stage


# -------- SAVE ANSWERS --------
def save_answer(user_id, key, value):
    if user_id in user_memory:
        user_memory[user_id]["answers"][key] = value


# -------- SAVE DOCUMENT ANALYSIS --------
def save_analysis(user_id, analysis):
    if user_id not in user_memory:
        user_memory[user_id] = {
            "messages": [],
            "stage": 1,
            "answers": {},
            "analysis": {}
        }

    user_memory[user_id]["analysis"] = analysis


# -------- GET DOCUMENT ANALYSIS --------
def get_analysis(user_id):
    if user_id in user_memory:
        return user_memory[user_id]["analysis"]
    return {}