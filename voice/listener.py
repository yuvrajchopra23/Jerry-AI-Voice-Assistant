import sounddevice as sd
import numpy as np
import tempfile
import os
import wave
import time
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 6
SILENCE_THRESHOLD = 500
MIN_AUDIO_LENGTH = 1

_is_muted = False

def mute():
    global _is_muted
    _is_muted = True

def unmute():
    global _is_muted
    _is_muted = False

def is_silent(audio_chunk):
    return np.abs(audio_chunk).mean() < SILENCE_THRESHOLD

def listen():
    if _is_muted:
        time.sleep(0.5)
        return None

    print("Listening...")
    audio_chunks = []
    silence_counter = 0
    speaking_started = False

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
        start_time = time.time()

        while True:
            if _is_muted:
                return None

            if time.time() - start_time > SILENCE_TIMEOUT:
                print("Timeout.")
                break

            chunk, _ = stream.read(SAMPLE_RATE // 4)
            audio_chunks.append(chunk.copy())

            if not is_silent(chunk):
                speaking_started = True
                silence_counter = 0
            else:
                if speaking_started:
                    silence_counter += 1
                    if silence_counter >= 4:
                        break

    if not speaking_started:
        return None

    audio_data = np.concatenate(audio_chunks, axis=0)

    if len(audio_data) < SAMPLE_RATE * MIN_AUDIO_LENGTH:
        return None

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language="en",
                response_format="text"
            )
        return transcription.strip() if transcription else None
    except Exception as e:
        print(f"[TRANSCRIPTION ERROR] {e}")
        return None
    finally:
        os.unlink(tmp_path)