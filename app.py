import requests
import json
import time

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
    "stream": True
}

start = time.time()
first_token_time = None

try:
    response = requests.post(
        OLLAMA_URL,
        json=data,
        stream=True
    )

    response.raise_for_status()

    print("MANU: ", end="", flush=True)

    for line in response.iter_lines():
        if not line:
            continue

        chunk = json.loads(line)

        if chunk.get("done"):
            break

        content = chunk.get("message", {}).get("content", "")

        if content:
            if first_token_time is None:
                first_token_time = time.time()

            print(content, end="", flush=True)

    end = time.time()

    print()

    if first_token_time:
        print(f"First response: {first_token_time - start:.2f} seconds")

    print(f"Total time: {end - start:.2f} seconds")

except requests.exceptions.RequestException as e:
    print("\nConnection error:", e)

except json.JSONDecodeError as e:
    print("\nJSON error:", e)