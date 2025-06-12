import zipfile
import sounddevice as sd
print(sd.query_devices())
import queue
import json
import sys
import urllib.request
import os
from vosk import Model, KaldiRecognizer

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
MODEL_ZIP = "vosk-model-en-us-0.22.zip"
MODEL_PATH = "vosk-model-en-us-0.22"
SAMPLE_RATE = 16000

q= queue.Queue()

if not os.path.exists(MODEL_PATH):
    print("Downloading Model")
    urllib.request.urlretrieve(MODEL_URL, MODEL_ZIP)

    print("Unzipping Model")
    with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
        zip_ref.extractall()

    os.remove(MODEL_ZIP)
    print("Model Ready")

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def main():
    print("Loading Model From", MODEL_PATH)
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    device_index = 1

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=16000, dtype='int16', channels=1, callback=audio_callback, device=device_index):
        print("Listening..... Say Stop Listening to stop.")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text","")
                if text:
                    print("You said:", text)
                    if text.lower() == "stop listening":
                        print("Stopping Listener")
                        break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by User")