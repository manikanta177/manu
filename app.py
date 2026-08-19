import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"

FAST_MODEL = "qwen3:1.7b"
THINK_MODEL = "qwen3:4b"

current_model = FAST_MODEL
thinking_enabled = False

messages = [
    {
        "role": "system",
        "content": (
            "You are MANU, a personal AI assistant. "
            "Be concise for simple questions and detailed only when necessary. "
            "Do not repeat the user's question. "
            "Avoid unnecessary introductions, excessive emojis, and long explanations. "
            "Give clear, direct and useful answers."
        )
    }
]

print("================================")
print("          MANU V0.2")
print("     Local Personal AI Agent")
print("================================")
print("Commands:")
print("/clear  - clear conversation")
print("/think  - switch to deep reasoning mode")
print("/fast   - switch to fast mode")
print("/exit   - exit MANU")
print()

while True:
    message = input("You: ").strip()

    if not message:
        continue

    # Exit
    if message.lower() == "/exit":
        print("MANU: Goodbye!")
        break

    # Clear conversation
    if message.lower() == "/clear":
        messages = [messages[0]]
        print("MANU: Conversation memory cleared.")
        print()
        continue

    # Enable deep reasoning
    if message.lower() == "/think":
        current_model = THINK_MODEL
        thinking_enabled = True
        print("MANU: Deep reasoning mode enabled.")
        print()
        continue

    # Enable fast mode
    if message.lower() == "/fast":
        current_model = FAST_MODEL
        thinking_enabled = False
        print("MANU: Fast mode enabled.")
        print()
        continue

    # Add user message to memory
    messages.append({
        "role": "user",
        "content": message
    })

    data = {
        "model": current_model,
        "messages": messages,
        "think": thinking_enabled,
        "stream": True
    }

    assistant_response = ""
    final_stats = None

    try:
        response = requests.post(
            OLLAMA_URL,
            json=data,
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        print(f"MANU ({current_model}): ", end="", flush=True)

        for line in response.iter_lines():
            if not line:
                continue

            chunk = json.loads(line)

            if chunk.get("done"):
                final_stats = chunk
                break

            content = chunk.get("message", {}).get("content", "")

            if content:
                print(content, end="", flush=True)
                assistant_response += content

        print()

        # Save assistant response
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Performance information
        if final_stats:
            total = final_stats.get("total_duration", 0) / 1_000_000_000
            load = final_stats.get("load_duration", 0) / 1_000_000_000
            prompt = final_stats.get("prompt_eval_duration", 0) / 1_000_000_000
            generation = final_stats.get("eval_duration", 0) / 1_000_000_000
            tokens = final_stats.get("eval_count", 0)

            print(
                f"[Total: {total:.2f}s | "
                f"Load: {load:.2f}s | "
                f"Prompt: {prompt:.2f}s | "
                f"Generation: {generation:.2f}s | "
                f"Tokens: {tokens}]"
            )

        print()

    except requests.exceptions.RequestException as e:
        print("\nMANU: Could not connect to Ollama.")
        print(f"Error: {e}")
        print()

        # Remove failed user message
        messages.pop()

    except json.JSONDecodeError:
        print("\nMANU: Could not understand Ollama's response.")
        print()

        messages.pop()