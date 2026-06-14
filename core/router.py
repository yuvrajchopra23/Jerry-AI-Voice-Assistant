from services.ai_service import ask_ai
from services.app_service import open_app
from services.web_service import open_website
from services.system_service import handle_system_command
from services.knowledge_service import calculate
from memory.memory_manager import add_to_history, learn_command, clear_history
from voice.speaker import speak
from ui.events import emit_message, emit_status, emit_typing
import threading

_voice_lock = threading.Lock()
_text_lock = threading.Lock()

def route(command: str, source: str = "text"):
    print(f"[ROUTE] command='{command}' source='{source}'")

    lock = _voice_lock if source == "voice" else _text_lock

    if not lock.acquire(blocking=False):
        print(f"[SKIP] Already processing {source} command.")
        return

    try:
        add_to_history("user", command)
        emit_message("user", command)
        emit_status("thinking")
        emit_typing(True)

        result = ask_ai(command)
        emit_typing(False)

        action   = result.get("action", "chat")
        target   = result.get("target", "")
        response = result.get("response", "")

        print(f"[ACTION] {action} → {target}")

        if action == "open_app":
            success = open_app(target)
            if not success:
                response = f"I couldn't find {target} on your system."

        elif action == "open_website":
            open_website(target)

        elif action == "system":
            system_response = handle_system_command(target)
            if system_response:
                response = system_response

        elif action == "calculate":
            response = calculate(target)

        elif action == "learn":
            if isinstance(target, dict):
                learn_command(target.get("phrase", ""), target.get("action", {}))

        elif action == "clear_history":
            clear_history()
            response = "Memory cleared."

        if response:
            add_to_history("assistant", response)
            emit_message("assistant", response)
            emit_status("ready")
            threading.Thread(target=speak, args=(response,), daemon=True).start()

    finally:
        emit_typing(False)
        emit_status("ready")
        lock.release()