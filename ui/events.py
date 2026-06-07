_socketio = None

def init_socketio(sio):
    global _socketio
    _socketio = sio

def emit_message(role: str, text: str):
    if _socketio:
        _socketio.emit("message", {"role": role, "text": text})

def emit_status(status: str):
    if _socketio:
        _socketio.emit("status", {"status": status})

def emit_typing(show: bool):
    if _socketio:
        _socketio.emit("typing", {"show": show})