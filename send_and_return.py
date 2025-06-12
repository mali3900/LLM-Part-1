import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

def send_to_api(input_text):
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": input_text}]}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}



if __name__ == "__main__":
    while True:
        input_text = input("Enter text")
        if input_text.lower() == "exit":
            break
        result = send_to_api(input_text)

        if "choices" in result and result["choices"]:
            reply = result["choices"][0]["message"]["content"]
            print("AI: " + reply)
        else:
            print("Error or unexpected response:", json.dumps(result, indent=2))
