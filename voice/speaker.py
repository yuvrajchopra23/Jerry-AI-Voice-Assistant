import pyttsx3

_speak_enabled = True

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
        from voice.listener import mute, unmute
        mute()                    # stop listening while speaking
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        unmute()                  # start listening again after speaking
    except Exception as e:
        print(f"[SPEECH ERROR] {e}")
        from voice.listener import unmute
        unmute()