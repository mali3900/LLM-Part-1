import sounddevice as sd
print(sd.query_devices())
import queue
import json
import sys
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-en-us-0.22"
SAMPLE_RATE = 16000
WAKE_WORD = "hello"

q = queue.Queue()

device_index = 1

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen_with_blocksize(recognizer, blocksize, device_index):
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=blocksize, dtype='int16', channels=1, callback=audio_callback, device=device_index):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                yield text

def listen_for_wake_word(recognizer):
    for text in listen_with_blocksize(recognizer, blocksize=5000, device_index=device_index):
        if WAKE_WORD in text:
            print("You Said", WAKE_WORD)
            return True
        if text == "stop listening":
            print("Stopping Listener")
            return False

def listen_for_command(recognizer):
    print("Listening for command")
    for text in listen_with_blocksize(recognizer, blocksize=16000, device_index=device_index):
        if text:
            print(f"command received, '{text}'")
            return True
        if text == "stop listening":
            print("Stopping Listener")
            return False

def main():
    print("Loading Model From", MODEL_PATH)

    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    print(f"Listening for the wake-word, '{WAKE_WORD}'")

    while True:
        if not listen_for_wake_word(recognizer):
           break
        if not listen_for_command(recognizer):
            break
        print(f"Back to waiting for wake word, '{WAKE_WORD}'\n")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by User")
