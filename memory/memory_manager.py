from db.mongo import memory_col
from config import CONVERSATION_HISTORY_LIMIT

_current_user_id = None

def set_current_user(user_id: str):
    global _current_user_id
    _current_user_id = user_id

def get_current_user():
    return _current_user_id

def load_memory():
    if not _current_user_id:
        return {"websites": {}, "apps": {}, "history": [], "learned_commands": {}}
    doc = memory_col.find_one({"user_id": _current_user_id})
    if not doc:
        return {"websites": {}, "apps": {}, "history": [], "learned_commands": {}}
    return doc

def save_memory(data):
    if not _current_user_id:
        return
    data.pop("_id", None)  # remove MongoDB _id before saving
    memory_col.update_one(
        {"user_id": _current_user_id},
        {"$set": data},
        upsert=True
    )

def add_to_history(role: str, content: str):
    if not _current_user_id:
        return
    memory_col.update_one(
        {"user_id": _current_user_id},
        {"$push": {"history": {
            "$each": [{"role": role, "content": content}],
            "$slice": -CONVERSATION_HISTORY_LIMIT
        }}},
        upsert=True
    )

def get_history():
    return load_memory().get("history", [])

def clear_history():
    if not _current_user_id:
        return
    memory_col.update_one(
        {"user_id": _current_user_id},
        {"$set": {"history": []}}
    )

def learn_command(phrase: str, action: dict):
    if not _current_user_id:
        return
    memory_col.update_one(
        {"user_id": _current_user_id},
        {"$set": {f"learned_commands.{phrase.lower().strip()}": action}},
        upsert=True
    )

def get_learned_commands():
    return load_memory().get("learned_commands", {})