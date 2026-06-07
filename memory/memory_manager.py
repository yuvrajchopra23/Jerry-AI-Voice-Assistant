import json
import os
from config import MEMORY_FILE, CONVERSATION_HISTORY_LIMIT

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"websites": {}, "apps": {}, "history": [], "learned_commands": {}}
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    data.setdefault("history", [])
    data.setdefault("learned_commands", {})
    data.setdefault("websites", {})
    data.setdefault("apps", {})
    return data

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_to_history(role: str, content: str):
    memory = load_memory()
    memory["history"].append({"role": role, "content": content})
    if len(memory["history"]) > CONVERSATION_HISTORY_LIMIT:
        memory["history"] = memory["history"][-CONVERSATION_HISTORY_LIMIT:]
    save_memory(memory)

def get_history():
    return load_memory().get("history", [])

def clear_history():
    memory = load_memory()
    memory["history"] = []
    save_memory(memory)

def learn_command(phrase: str, action: dict):
    memory = load_memory()
    memory["learned_commands"][phrase.lower().strip()] = action
    save_memory(memory)

def get_learned_commands():
    return load_memory().get("learned_commands", {})