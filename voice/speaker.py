import pyttsx3
from config import SPEAK_ENABLED

_speak_enabled = SPEAK_ENABLED

def set_speak(enabled: bool):
    global _speak_enabled
    _speak_enabled = enabled

def get_speak():
    return _speak_enabled

def speak(text):
    print("Jerry:", text)
    if not _speak_enabled:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[SPEECH ERROR] {e}")