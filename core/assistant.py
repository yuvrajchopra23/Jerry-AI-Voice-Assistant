from voice.listener import listen
from voice.speaker import speak
from voice.wake_word import wait_for_wake
from core.router import route
from services.ai_service import switch_mode, get_mode
from ui.server import start_ui
from ui.events import emit_status
from config import ACTIVE_TIMEOUT
import threading
import time

def text_input_loop():
    while True:
        try:
            command = input("You (text): ").strip()
            if not command:
                continue
            if command.lower().startswith("switch to"):
                mode = command.lower().replace("switch to", "").strip()
                print(switch_mode(mode))
            else:
                route(command)
        except Exception as e:
            print(f"[TEXT INPUT ERROR] {e}")

def run():
    print("🟢 Jerry is online")
    print(f"🤖 AI mode: {get_mode()}")
    print("🌐 Dashboard → http://127.0.0.1:5000\n")

    ui_thread = threading.Thread(target=start_ui, daemon=True)
    ui_thread.start()

    text_thread = threading.Thread(target=text_input_loop, daemon=True)
    text_thread.start()

    while True:
        emit_status("sleeping")
        wait_for_wake()
        emit_status("listening")
        speak("Yes sir")

        last_active = time.time()

        while True:
            if time.time() - last_active > ACTIVE_TIMEOUT:
                speak("Going to sleep")
                emit_status("sleeping")
                break

            emit_status("listening")
            command = listen()

            if not command:
                continue

            command = command.lower().strip()
            print(f"You (voice): {command}")
            last_active = time.time()

            if "exit" in command or "goodbye" in command:
                speak("Goodbye sir")
                exit()

            if "switch to groq" in command:
                speak(switch_mode("groq"))
                continue
            if "switch to ollama" in command:
                speak(switch_mode("ollama"))
                continue

            emit_status("thinking")
            route(command)