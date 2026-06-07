import subprocess
import re

# ── Volume ──────────────────────────────────────────────────────
def set_volume(level: int) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level} percent."
    except Exception as e:
        return f"Couldn't set volume: {e}"


def mute_volume() -> str:
    return set_volume(0)


# ── Brightness ──────────────────────────────────────────────────
def set_brightness(level: int) -> str:
    try:
        subprocess.run(
            f'powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})',
            shell=True,
            capture_output=True
        )
        return f"Brightness set to {level} percent."
    except Exception as e:
        return f"Couldn't set brightness: {e}"


# ── Power ───────────────────────────────────────────────────────
def shutdown() -> str:
    subprocess.run("shutdown /s /t 5", shell=True)
    return "Shutting down in 5 seconds."

def restart() -> str:
    subprocess.run("shutdown /r /t 5", shell=True)
    return "Restarting in 5 seconds."

def sleep() -> str:
    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
    return "Going to sleep."


# ── Main handler ────────────────────────────────────────────────
def handle_system_command(command: str) -> str:
    """
    Accepts either:
    - Natural language: "volume to 50", "shutdown", "mute"
    - AI formatted:     "volume:50", "brightness:70"
    """
    command = command.lower().strip()

    # AI format: "volume:50" or "brightness:70"
    if ":" in command:
        key, _, val = command.partition(":")
        key = key.strip()
        val = val.strip()
        if key == "volume" and val.isdigit():
            return set_volume(int(val))
        if key == "brightness" and val.isdigit():
            return set_brightness(int(val))

    # Volume
    match = re.search(r'volume\s+(?:to\s+)?(\d+)', command)
    if match:
        return set_volume(int(match.group(1)))
    if "volume up" in command or "increase volume" in command:
        return set_volume(80)
    if "volume down" in command or "decrease volume" in command:
        return set_volume(30)
    if "mute" in command:
        return mute_volume()

    # Brightness
    match = re.search(r'brightness\s+(?:to\s+)?(\d+)', command)
    if match:
        return set_brightness(int(match.group(1)))
    if "brightness up" in command or "increase brightness" in command:
        return set_brightness(80)
    if "brightness down" in command or "decrease brightness" in command:
        return set_brightness(30)

    # Power
    if "shutdown" in command or "shut down" in command:
        return shutdown()
    if "restart" in command or "reboot" in command:
        return restart()
    if "sleep" in command:
        return sleep()

    return "I didn't understand that system command."