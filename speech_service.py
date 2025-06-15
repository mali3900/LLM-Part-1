# new speech_service.py
import torch
from TTS.api import TTS
import time

# Check if a CUDA-enabled GPU is available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"TTS using device: {device}")

# Initialize the TTS model
# This will download the model on the first run
# Model: "tts_models/en/ljspeech/vits" is a popular, high-quality female voice.
# Model: "tts_models/en/vctk/vits_cmu-arctic-xvectors" can do multi-speaker voices.
print("Loading TTS model...")
tts = TTS("tts_models/en/ljspeech/vits").to(device)
print("TTS model loaded.")

is_speaking = False


def speak(text):
    global is_speaking
    is_speaking = True

    print(f">>> {text}")
    # The 'speaker_wav' argument is used for zero-shot voice cloning, which you can explore later.
    # For a single-speaker model like ljspeech, you don't need it.
    tts.tts_to_file(text=text, file_path="output.wav")

    # This part requires a library to play the wav file, like sounddevice or simpleaudio
    # For simplicity, we'll continue using sounddevice as your project already has it.
    import soundfile as sf
    import sounddevice as sd

    data, fs = sf.read('output.wav', dtype='float32')
    sd.play(data, fs)
    sd.wait()  # Wait until the file is done playing

    is_speaking = False
    time.sleep(0.2)