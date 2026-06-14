import webbrowser
import os
from voice.speaker import speak
from memory.memory_manager import load_memory, save_memory

# Register Opera
OPERA_PATH = r"C:\Users\yuvra\AppData\Local\Programs\Opera\opera.exe"

if os.path.exists(OPERA_PATH):
    webbrowser.register('opera', None, webbrowser.BackgroundBrowser(OPERA_PATH))
    BROWSER = webbrowser.get('opera')
else:
    print("[WARN] Opera not found, using default browser")
    BROWSER = webbrowser.get()

def sanitize_url_name(name: str) -> str:
    return name.lower().replace(" ", "")


def open_url(url: str):
    try:
        BROWSER.open(url)
    except Exception as e:
        print(f"[ERROR] Could not open URL: {e}")
        os.startfile(url)

def open_website(target: str):
    memory = load_memory()
    name_key = target.lower().strip()

    # Check memory first
    if name_key in memory["websites"]:
        url = memory["websites"][name_key]
        open_url(url)
        speak(f"Opening {name_key}")
        return

    url = build_url(target)
    print(f"[DEBUG] Opening URL: {url}")
    open_url(url)

    memory["websites"][name_key] = url
    save_memory(memory)
    speak(f"Opening {name_key}")

def build_url(target: str) -> str:
    target = target.strip()

    if target.startswith(("http://", "https://")):
        return target

    return f"https://www.{sanitize_url_name(target)}.com"