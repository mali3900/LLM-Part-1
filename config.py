import os
import queue
from dotenv import load_dotenv

load_dotenv()

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.21.zip"
MODEL_PATH = "vosk-model-en-us-0.21"
MODEL_ZIP = "vosk-model-en-us-0.21.zip"
CACHE_FILE = ".input_device_cache"

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

SAMPLE_RATE = 16000
WAKE_WORD = "celeste"

audio_queue = queue.Queue()