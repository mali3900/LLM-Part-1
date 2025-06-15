import json
import os
from datetime import datetime

MEMORY_FILE = "memory_log.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def store_memory(key, value):
    memory = load_memory()

    entry =  {"timestamp": datetime.now().isoformat(), "key":key, "value":value}

    memory.append(entry)
    save_memory(memory)