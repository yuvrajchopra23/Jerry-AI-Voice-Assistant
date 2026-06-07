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
SILENCE_TIMEOUT = 6      # stop listening after 6s of silence
SILENCE_THRESHOLD = 500  # audio level below this = silence
MIN_AUDIO_LENGTH = 1     # minimum seconds of audio before transcribing

def is_silent(audio_chunk):
    return np.abs(audio_chunk).mean() < SILENCE_THRESHOLD

def listen():
    print("Listening...")

    audio_chunks = []
    silence_counter = 0
    speaking_started = False

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
        start_time = time.time()

        while True:
            # Hard timeout
            if time.time() - start_time > SILENCE_TIMEOUT:
                print("Timeout.")
                break

            chunk, _ = stream.read(SAMPLE_RATE // 4)  # 0.25s chunks
            audio_chunks.append(chunk.copy())

            if not is_silent(chunk):
                speaking_started = True
                silence_counter = 0
            else:
                if speaking_started:
                    silence_counter += 1
                    # Stop after 1 second of silence after speech
                    if silence_counter >= 4:
                        break

    if not speaking_started:
        return None

    # Combine all chunks
    audio_data = np.concatenate(audio_chunks, axis=0)

    # Need at least MIN_AUDIO_LENGTH seconds
    if len(audio_data) < SAMPLE_RATE * MIN_AUDIO_LENGTH:
        return None

    # Save to temp wav file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    # Transcribe with Groq Whisper
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
        os.unlink(tmp_path)  # delete temp file