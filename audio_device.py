import os
import sounddevice as sd
from config import CACHE_FILE

def choose_input_device():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cached_index = f.read().strip()
            if cached_index.isdigit():
                print(f"Using cached input device index: {cached_index}")
                return int(cached_index)

    print("Choose input device:")
    devices = sd.query_devices()
    input_devices = []
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{idx}: {dev['name']}")
            input_devices.append((idx, dev))

    while True:
        try:
            choice = int(input("Choose input device: "))
            device_info = devices[choice]
            if device_info.get("max_input_channels", 0) > 0:
                with open(CACHE_FILE, "w") as f:
                    f.write(str(choice))
                return choice
            else:
                print("The selected device has no input channels.")
        except (ValueError, IndexError):
            print("Invalid input. Please choose a valid device index.")