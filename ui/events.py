_socketio = None
_active_sid = None

def init_socketio(sio):
    global _socketio
    _socketio = sio

def set_active_sid(sid):
    global _active_sid
    _active_sid = sid

def emit_message(role: str, text: str):
    if _socketio and _active_sid:
        _socketio.emit("message", {"role": role, "text": text}, to=_active_sid)

def emit_status(status: str):
    if _socketio and _active_sid:
        _socketio.emit("status", {"status": status}, to=_active_sid)

def emit_typing(show: bool):
    if _socketio and _active_sid:
        _socketio.emit("typing", {"show": show}, to=_active_sid)