from vosk import Model, KaldiRecognizer
from model_manager import download_and_setup_model
from audio_device import choose_input_device
from listener import listen_for_wake_and_command
from speech_service import speak
from config import MODEL_PATH, SAMPLE_RATE


def main():
    download_and_setup_model()

    device_index = choose_input_device()

    print(f"Loading Model From {MODEL_PATH}")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    while True:
        listen_for_wake_and_command(recognizer, device_index)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping application.")
        speak("Stopped by User")