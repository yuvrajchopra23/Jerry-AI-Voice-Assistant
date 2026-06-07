import re
import os
import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, OLLAMA_MODEL, DEFAULT_AI_MODE
from memory.memory_manager import get_history, get_learned_commands

SYSTEM_PROMPT = """
You are Jerry, a smart desktop voice assistant. You are helpful, concise, and friendly.
You respond in short sentences since your responses are spoken aloud.

You can perform these actions by responding in this exact JSON format:
{{
  "action": "open_app" | "open_website" | "system" | "calculate" | "answer" | "learn" | "chat" | "clear_history",
  "target": "<app name, url, system command, math expression, or answer>",
  "response": "<what you say to the user out loud>"
}}

Actions explained:
- open_app     : open a desktop application. target = app name e.g. "chrome"
- open_website : open a website. target = full url e.g. "https://www.youtube.com"
- system       : system control. target = "volume:50" | "brightness:70" | "shutdown" | "restart" | "sleep" | "mute"
- calculate    : math. target = clean math expression e.g. "25*4+10"
- answer       : answer a factual question. target = the answer text
- learn        : remember a new command. target = {{"phrase": "...", "action": {{...}}}}
- chat         : general conversation. target = ""
- clear_history: wipe conversation memory. target = ""

Rules:
- ALWAYS respond with valid JSON only. No text outside the JSON.
- For websites always build the full https:// url yourself.
- For calculations convert word numbers to digits yourself before putting in target.
- Keep response short — it will be spoken aloud.

Learned commands: {learned}
""".strip()

current_mode = DEFAULT_AI_MODE
client = Groq(api_key=GROQ_API_KEY)


def get_system_prompt() -> str:
    learned = get_learned_commands()
    return SYSTEM_PROMPT.format(learned=str(learned))


def switch_mode(mode: str) -> str:
    global current_mode
    if mode in ("groq", "ollama"):
        current_mode = mode
        return f"Switched to {mode} mode."
    return "Unknown mode. Say groq or ollama."


def get_mode() -> str:
    return current_mode


# ── Groq ────────────────────────────────────────────────────────
def ask_groq(user_message: str) -> str:
    history = get_history()

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=500,
        messages=messages
    )
    return response.choices[0].message.content.strip()


# ── Ollama ──────────────────────────────────────────────────────
def ask_ollama(user_message: str) -> str:
    try:
        import ollama
        history = get_history()

        messages = [{"role": "system", "content": get_system_prompt()}]
        messages += history
        messages.append({"role": "user", "content": user_message})

        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
        return response["message"]["content"].strip()
    except Exception as e:
        return f'{{"action": "chat", "target": "", "response": "Ollama error: {e}"}}'


# ── Main entry ──────────────────────────────────────────────────
def ask_ai(user_message: str) -> dict:
    try:
        if current_mode == "groq":
            raw = ask_groq(user_message)
        else:
            raw = ask_ollama(user_message)

        print(f"[AI RAW] {raw}")

        # Extract JSON safely even if model adds extra text
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return {"action": "chat", "target": "", "response": raw}

    except json.JSONDecodeError:
        return {"action": "chat", "target": "", "response": "I had trouble understanding that."}
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return {"action": "chat", "target": "", "response": "Sorry, something went wrong."}