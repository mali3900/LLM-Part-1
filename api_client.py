import requests
from datetime import datetime
from config import API_URL, HEADERS
from speech_service import speak


def get_ai_response(command):
    today_date = datetime.now().strftime("%B %d, %Y")

    payload = {
        "model": "gpt-4.1-mini",
        "tools": [{"type": "web_search_preview"}],
        "instructions": f"You are jarvis, a genius AI system that has the ability to assist Lucas and guests of Lucas's house with their tasks and questions. Today's date: {today_date}",
        "max_output_tokens": 1000,
        "user": "Lucas",
        "input": command,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        reply = data.get("output", [{}])[0].get("content", "Sorry, no reply.")[0]['text']
        print(f"[AI] {reply} ")
        speak(reply)

    except requests.exceptions.RequestException as e:
        error_message = f'API Error: {str(e)}'
        print(error_message)
        speak("I encountered an error trying to process your request.")