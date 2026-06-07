import re

def detect_intent(text):
    text = text.lower().strip()

    # Open/launch/start → always ACTION
    if text.startswith(("open", "launch", "start")):
        return "ACTION"

    # Explicit calc keyword OR math expression
    if "calculate" in text or "compute" in text or re.search(r'\d+\s*[\+\-\*\/]\s*\d+', text):
        return "CALC"

    # Wikipedia / factual questions
    if any(text.startswith(p) for p in ("what is", "who is", "when is", "where is", "tell me about")):
        return "QUESTION"

    # Time / date shortcuts
    if "time" in text or "date" in text or "day" in text:
        return "QUESTION"

    return "CHAT"