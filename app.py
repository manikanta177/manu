import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"

message = input("You: ")

data = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": message
        }
    ],
    "stream": False
}

response = requests.post(OLLAMA_URL, json=data)

result = response.json()

print("MANU:", result["message"]["content"])