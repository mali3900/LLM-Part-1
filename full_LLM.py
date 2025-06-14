import time
import sounddevice as sd
import queue
import json
import sys
import pyttsx3
import zipfile
import urllib.request
import os
import requests
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
from keyword_listener import device_index


#######################################################################

load_dotenv()

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.21.zip"
MODEL_PATH = "vosk-model-en-us-0.21"
MODEL_ZIP = "vosk-model-en-us-0.21.zip"

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

SAMPLE_RATE = 16000
WAKE_WORD = "jarvis"

q = queue.Queue()

is_speaking = False

#######################################################################

def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = downloaded * 100 / total_size if total_size > 0 else 0
    bar_length = 40
    filled_length = int(bar_length * percent // 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rDownloading: |{bar}| {percent:.2f}%')
    sys.stdout.flush()

if not os.path.exists(MODEL_PATH):
    print("Downloading Model")
    urllib.request.urlretrieve(MODEL_URL, MODEL_ZIP, reporthook=show_progress)
    print("\nUnzipping Model")
    with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
        zip_ref.extractall()
    os.remove(MODEL_ZIP)
    print("Model Ready")

engine = pyttsx3.init()  # Automatically picks the correct driver for your OS

#######################################################################

def choose_input_device():
    print("Choose input device")
    devices = sd.query_devices()
    print(type(devices[3]))
    print(devices[3])

    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{idx}: {dev['name']}")
    while True:
        try:
            idex = int(input("Choose input device: "))
            device_info = devices[idex]

            max_input_channels = device_info.get("max_input_channels", 0)

            if max_input_channels > 0:
                return idex
            else:
                print("No input channels found on device")
        except (ValueError, IndexError):
            print("Invalid input")

def speak(text):
    global is_speaking
    is_speaking = True
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()
    is_speaking = False
    time.sleep(0.2)
    print(f">>> {text}")

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if not is_speaking:
        q.put(bytes(indata))

def listen_for_wake_and_command(recognizer):
    print("Listening...")
    heard_hello = False
    collected = ""
    last_speech_time = time.time()
    silence_timeout = 2.5

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=2000, dtype='int16',
                           channels=1, callback=audio_callback, device=device_index):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()
                if not text:
                    continue

                print(f"[USER SAID] {text}")
                last_speech_time = time.time()

                if not heard_hello:
                    if WAKE_WORD in text:
                        heard_hello = True
                        text_after = text.split(WAKE_WORD, 1)[-1].strip()
                        collected += text_after + " "
                else:
                    collected += text + " "
            else:
                partial = json.loads(recognizer.PartialResult())
                if partial.get("partial"):
                    last_speech_time = time.time()

            if heard_hello and (time.time() - last_speech_time > silence_timeout):
                break

    cleaned = collected.strip()
    if not cleaned:
        speak("No command heard.")
        return True

    print(f"[FINAL COMMAND] {cleaned}")

    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": cleaned}], "temperature": 0.7}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, no reply.")
        print(f"[AI] {reply} ")
        speak(reply)

    except requests.exceptions.RequestException as e:
        print('error: ' + str(e))
        return {"error": str(e)}

    return True

#######################################################################

def main():
    global device_index
    device_index = choose_input_device()

    print("Loading Model From", MODEL_PATH)
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    speak(f"Listening for the wake-word, '{WAKE_WORD}'")

    while True:
        if not listen_for_wake_and_command(recognizer):
           break
        speak(f"Back to waiting for wake word, '{WAKE_WORD}'")

#######################################################################

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Stopped by User")