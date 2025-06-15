import pyttsx3
import time

engine = pyttsx3.init()
is_speaking = False

def speak(text):
    global is_speaking
    is_speaking = True
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty("voice", voices[132].id)
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()
    is_speaking = False
    time.sleep(0.2)
    print(f">>> {text}")