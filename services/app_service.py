import subprocess
import os
from rapidfuzz import process
from voice.speaker import speak
from memory.memory_manager import load_memory, save_memory
from config import DESKTOP, START_MENU

SKIP_DIRS = [
    "startup",
    "accessories",
    "maintenance", 
    "system tools",
]

SKIP_NAMES = [
    "send to onenote",
    "onenote",
    "desktop.ini",
    "uninstall",
    "help",
    "readme",
]

# All folders to scan for apps
SCAN_DIRS = [
    DESKTOP,
    START_MENU,
    # Regular Start Menu for all users
    os.path.join(os.environ.get("PROGRAMDATA", ""), 
                 "Microsoft", "Windows", "Start Menu", "Programs"),
    # Store apps shortcuts live here
    os.path.join(os.environ.get("APPDATA", ""),
                 "Microsoft", "Windows", "Start Menu", "Programs"),
]

def get_apps():
    apps = {}

    for directory in SCAN_DIRS:
        if not directory or not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            folder_name = os.path.basename(root).lower()
            if any(skip in folder_name for skip in SKIP_DIRS):
                continue

            for file in files:
                if file.endswith(".lnk") or file.endswith(".exe"):
                    name = file.replace(".lnk", "").replace(".exe", "").lower().strip()

                    if any(skip in name for skip in SKIP_NAMES):
                        continue

                    full_path = os.path.join(root, file)
                    apps[name] = full_path
                    print(f"[SCAN] Found app: {name}")  # remove later

    return apps

APP_DB = get_apps()

def open_app(name):
    name = name.lower().strip()

    # Check learned memory first
    memory = load_memory()
    if name in memory.get("apps", {}):
        path = memory["apps"][name]
        subprocess.Popen(f'explorer "{path}"', shell=True)
        speak(f"Opening {name}")
        return True

    if not APP_DB:
        return False

    match = process.extractOne(name, APP_DB.keys(), score_cutoff=70)

    if match:
        app_name, score, _ = match
        print(f"[DEBUG] Matched: '{app_name}' (score: {score})")
        path = APP_DB[app_name]

        # Use explorer for .lnk files, Popen for .exe
        if path.endswith(".lnk"):
            subprocess.Popen(f'explorer "{path}"', shell=True)
        else:
            subprocess.Popen(path, shell=True)

        speak(f"Opening {app_name}")
        memory["apps"][name] = path
        save_memory(memory)
        return True

    return False