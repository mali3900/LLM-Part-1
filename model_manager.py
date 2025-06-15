import os
import sys
import urllib.request
import zipfile
from config import MODEL_PATH, MODEL_URL, MODEL_ZIP

def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = downloaded * 100 / total_size if total_size > 0 else 0
    bar_length = 40
    filled_length = int(bar_length * percent // 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rDownloading: |{bar}| {percent:.2f}%')
    sys.stdout.flush()

def download_and_setup_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading Model")
        urllib.request.urlretrieve(MODEL_URL, MODEL_ZIP, reporthook=show_progress)
        print("\nUnzipping Model")
        with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
            zip_ref.extractall()
        os.remove(MODEL_ZIP)
        print("Model Ready")