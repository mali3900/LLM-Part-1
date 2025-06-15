import sounddevice as sd
import json
import sys
import time
from config import SAMPLE_RATE, WAKE_WORD, audio_queue
from speech_service import speak, is_speaking
from api_client import get_ai_response

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if not is_speaking:
        audio_queue.put(bytes(indata))

def listen_for_wake_and_command(recognizer, device_index):
    print("Listening...")
    heard_wake_word = False
    command_text = ""
    last_speech_time = time.time()
    silence_timeout = 2.5
    speak(f"Listening for the wake-word, '{WAKE_WORD}'")

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=2000, dtype='int16',
                           channels=1, callback=audio_callback, device=device_index):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()

                if text:
                    print(f"[USER SAID] {text}")
                    last_speech_time = time.time()
                    if not heard_wake_word:
                        if WAKE_WORD in text:
                            heard_wake_word = True
                            text_after_wake_word = text.split(WAKE_WORD, 1)[-1].strip()
                            command_text += text_after_wake_word + " "
                    else:
                        command_text += text + " "
            else:
                partial_result = json.loads(recognizer.PartialResult())
                if partial_result.get("partial"):
                    last_speech_time = time.time()

            if heard_wake_word and (time.time() - last_speech_time > silence_timeout):
                break

    cleaned_command = command_text.strip()
    if not cleaned_command:
        speak("No command was heard after the wake word.")
        return

    print(f"[FINAL COMMAND] {cleaned_command}")
    get_ai_response(cleaned_command)