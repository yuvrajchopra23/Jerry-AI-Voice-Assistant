import pvporcupine
import sounddevice as sd
import struct
import winsound

ACCESS_KEY = "W7PdWadZUdfjpE8aAqsoajrdHXBTpeQuICbF5eUi65yUSAdmBXsVgw==" 

porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=["hello-jerry_en_windows_v4_0_0.ppn"]
)

def wait_for_wake():
    with sd.InputStream(
        samplerate=porcupine.sample_rate,
        channels=1,
        dtype="int16",
        blocksize=porcupine.frame_length
    ) as stream:
        print("Waiting for wake word...")

        while True:
            pcm, _ = stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm) >= 0:
                winsound.Beep(800, 200)
                return