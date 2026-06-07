from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from services.ai_service import switch_mode, get_mode
from services.system_service import handle_system_command
from memory.memory_manager import get_history, clear_history
from ui.events import init_socketio, emit_message
import threading
from voice.speaker import set_speak, get_speak

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = "jerry-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize shared emitter
init_socketio(socketio)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return jsonify(get_history())

@app.route("/mode")
def mode():
    return jsonify({"mode": get_mode()})

@socketio.on("user_message")
def handle_message(data):
    from core.router import route
    command = data.get("text", "").strip()
    if not command:
        return
    socketio.emit("status", {"status": "thinking"})
    threading.Thread(target=route, args=(command,), daemon=True).start()

@socketio.on("switch_mode")
def handle_switch(data):
    mode = data.get("mode", "groq")
    result = switch_mode(mode)
    emit("mode_switched", {"mode": mode, "message": result})

@socketio.on("system_command")
def handle_system(data):
    cmd = data.get("command", "")
    result = handle_system_command(cmd)
    emit_message("system", result or "Done.")

@socketio.on("clear_history")
def handle_clear():
    clear_history()
    emit("history_cleared")

def start_ui():
    socketio.run(app, host="127.0.0.1", port=5000, debug=False, use_reloader=False)

@socketio.on("toggle_speak")
def handle_toggle_speak(data):
    enabled = data.get("enabled", True)
    set_speak(enabled)
    emit("speak_toggled", {"enabled": enabled})