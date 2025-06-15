import requests
from datetime import datetime
from config import API_URL, HEADERS
from speech_service import speak

memory_block = "{'memory': {'key': 'some_key', 'value': 'some_value'}}"


def get_ai_response(command, previous_message_id):
    today_date = datetime.now().strftime("%B %d, %Y")

    payload = {
        "model": "gpt-4.1-mini",
        "tools": [{"type": "web_search_preview"}],
        "instructions": f"You are celeste, a genius AI system that has the ability to assist Lucas and guests of Lucas's house with their tasks and questions. DO NOT format any responses. Everything you send will be spoken out loud so please use sentences. After responding, decide whether to save something to memory by returning a second block with: {memory_block}. , Today's date: {today_date}",
        "max_output_tokens": 1000,
        "user": "Lucas",
        "input": command,
        "temperature": 0.7
    }

    if previous_message_id != "":
        payload["previous_response_id"] = previous_message_id
    print(payload)

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        error_message = f'API Error: {str(e)}'
        print(error_message)
        speak("I encountered an error trying to process your request.")