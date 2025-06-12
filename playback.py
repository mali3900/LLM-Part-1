import pyttsx3
import re


def play_music(song):
    default_keywords = ["music", "playlist", "songs", "something"]
    if song.strip() in default_keywords:
        return "Playing default playlist"
    else:
        return "Playing" + song

def run_commands(command):
    if command in ["exit", "leave", "quit"]:
        return "exit"
    if command.startswith("play"):
        match = re.match(r"play(?: (.+))", command)
        if match:
            song = match.group(1)
            return play_music(song)
        else:
            return "Didn't recognize play command"
    else:
        return "No command for" + text


def process_text(text):
    return run_commands(text.lower())

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    while True:
        text = input("Enter your text: ")
        output = process_text(text)
        if output == "exit":
            speak("leaving")
            break

        speak(output)