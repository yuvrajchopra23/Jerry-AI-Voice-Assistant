from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from services.ai_service import switch_mode, get_mode
from services.system_service import handle_system_command
from memory.memory_manager import get_history, clear_history, set_current_user
from auth.auth_routes import auth_bp
from auth.auth_utils import verify_token
from ui.events import init_socketio, emit_message, set_active_sid
import threading

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = "jerry-secret-key-2024"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    ping_timeout=60,
    ping_interval=25
)

init_socketio(socketio)

authenticated_users = {}

app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return jsonify(get_history())

@app.route("/mode")
def mode():
    return jsonify({"mode": get_mode()})

@socketio.on("connect")
def handle_connect():
    print(f"[SOCKET] Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    authenticated_users.pop(request.sid, None)
    print(f"[SOCKET] Client disconnected: {request.sid}")

@socketio.on("authenticate")
def handle_auth(data):
    token = data.get("token", "")
    payload = verify_token(token)
    if not payload:
        emit("auth_error", {"error": "Invalid or expired token."})
        return

    authenticated_users[request.sid] = {
        "user_id": payload["user_id"],
        "username": payload["username"]
    }
    set_current_user(payload["user_id"])
    set_active_sid(request.sid)
    print(f"[AUTH] {payload['username']} authenticated (sid: {request.sid})")

    emit("auth_success", {
        "username": payload["username"],
        "user_id": payload["user_id"]
    })

@socketio.on("user_message")
def handle_message(data):
    from core.router import route
    command = data.get("text", "").strip()
    if not command:
        return

    user = authenticated_users.get(request.sid)
    if user:
        set_current_user(user["user_id"])
        set_active_sid(request.sid)

    print(f"[MESSAGE] '{command}' from {user}")
    emit("status", {"status": "thinking"})
    threading.Thread(target=route, args=(command, "text"), daemon=True).start()

@socketio.on("system_command")
def handle_system(data):
    cmd = data.get("command", "")
    print(f"[SYSTEM] Command: {cmd}")
    result = handle_system_command(cmd)
    emit("message", {"role": "system", "text": result or "Done."})

@socketio.on("toggle_speak")
def handle_toggle_speak(data):
    from voice.speaker import set_speak
    enabled = data.get("enabled", True)
    set_speak(enabled)
    emit("speak_toggled", {"enabled": enabled})

@socketio.on("clear_history")
def handle_clear():
    user = authenticated_users.get(request.sid)
    if user:
        set_current_user(user["user_id"])
    clear_history()
    emit("history_cleared")

@socketio.on("switch_mode")
def handle_switch(data):
    mode = data.get("mode", "groq")
    result = switch_mode(mode)
    emit("mode_switched", {"mode": mode, "message": result})

def start_ui():
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)

@app.route("/command", methods=["POST"])
def handle_command():
    import core.router as router
    from flask import request, jsonify

    data = request.get_json(silent=True) or {}
    command = data.get("text", "").strip()

    if not command:
        return jsonify({"response": "Empty command."}), 400

    print(f"[WIDGET] Command: {command}")

    response_holder = []

    # Save original functions
    original_emit_message = router.emit_message
    original_emit_status = router.emit_status
    original_emit_typing = router.emit_typing

    # Capture assistant response while still forwarding events
    def capture_emit_message(role, text):
        print(f"[CAPTURE] {role}: {text}")

        if role == "assistant":
            response_holder.append(text)

        original_emit_message(role, text)

    def capture_emit_status(status):
        original_emit_status(status)

    def capture_emit_typing(value):
        original_emit_typing(value)

    try:
        # Patch router's imported functions
        router.emit_message = capture_emit_message
        router.emit_status = capture_emit_status
        router.emit_typing = capture_emit_typing

        # Execute the command
        router.route(command, "text")

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"response": str(e)}), 500

    finally:
        # Restore originals
        router.emit_message = original_emit_message
        router.emit_status = original_emit_status
        router.emit_typing = original_emit_typing

    response = response_holder[0] if response_holder else "Done."

    print(f"[WIDGET RESPONSE] {response}")

    return jsonify({"response": response}), 200