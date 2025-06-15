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
    """
    Listens for a wake word and then captures a command until a pause is detected.

    Args:
        recognizer: An initialized voice recognition object (e.g., from Vosk).
        device_index: The audio input device index for sounddevice.
    """
    print("Initializing listener...")
    heard_wake_word = False
    command_text = ""
    previous_message_id = ""
    last_speech_time = time.time()

    # --- TIMEOUT CONFIGURATION ---
    # How long to wait in "conversation mode" before requiring the wake word again.
    conversation_timeout = 20
    # How long of a pause indicates the user has finished their command.
    # This is the crucial new variable.
    command_pause_threshold = 2.0

    print(f"Listening for the wake-word, '{WAKE_WORD}'...")

    # Using sounddevice's RawInputStream to get raw audio data for the recognizer
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=2000, dtype='int16',
                           channels=1, callback=audio_callback, device=device_index):
        while True:
            # The main loop now has three primary responsibilities:
            # 1. Process incoming audio.
            # 2. Check if a command has concluded (short pause).
            # 3. Check if the entire conversation has timed out (long pause).

            # --- 1. Process Incoming Audio ---
            if is_speaking:
                time.sleep(0.1) # Sleep briefly to avoid busy-waiting
                continue
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()

                if text:
                    print(f"[USER SAID] {text}")
                    last_speech_time = time.time() # Update time on any detected speech

                    if not heard_wake_word:
                        if WAKE_WORD in text:
                            print("✅ Wake word detected! Now listening for your command.")
                            heard_wake_word = True
                            # Capture any text spoken immediately after the wake word
                            text_after_wake_word = text.split(WAKE_WORD, 1)[-1].strip()
                            if text_after_wake_word:
                                command_text += text_after_wake_word + " "
                    else:
                        # We are in conversation mode, so append all speech
                        command_text += text + " "
            else:
                # This block handles partial results, which is good for keeping
                # the `last_speech_time` updated even if the user mumbles.
                partial_result = json.loads(recognizer.PartialResult())
                if partial_result.get("partial"):
                    last_speech_time = time.time()


            # --- 2. Check for Command Completion ---
            cleaned_command = command_text.strip()
            # This logic is now outside the audio processing block.
            # It checks if we are in command mode AND the user has paused speaking.
            if heard_wake_word and (time.time() - last_speech_time > command_pause_threshold) and cleaned_command:
                print(f"[FINAL COMMAND CAPTURED] {cleaned_command}")

                # --- Process the completed command ---
                response_data = get_ai_response(cleaned_command, previous_message_id)
                previous_message_id = response_data['id']
                print(previous_message_id)
                # Safely access the nested reply
                try:
                    reply = response_data["output"][0]["content"][0]["text"]
                except (IndexError, KeyError):
                    reply = "Sorry, I couldn't process the response."

                print(f"[AI REPLY] {reply}")
                speak(reply)

                # --- Reset for the next command IN THE SAME CONVERSATION ---
                command_text = ""
                # We update last_speech_time here so the conversation_timeout
                # gives the user time to ask a follow-up question.
                last_speech_time = time.time()


            # --- 3. Check for Conversation Timeout ---
            # If the user is silent for too long, exit "conversation mode".
            if heard_wake_word and (time.time() - last_speech_time > conversation_timeout):
                print(f"Conversation timed out. Resetting to listen for wake word.")
                # Reset all conversational state
                heard_wake_word = False
                command_text = ""
                previous_message_id = ""