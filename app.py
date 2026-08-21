import requests
import json
import os

OLLAMA_URL = "http://localhost:11434/api/chat"

FAST_MODEL = "qwen3:1.7b"
THINK_MODEL = "qwen3:4b"

MEMORY_FILE = "memory.json"

current_model = FAST_MODEL
thinking_enabled = False


# ==============================
# MEMORY FUNCTIONS
# ==============================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    return []


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=2, ensure_ascii=False)


# ==============================
# SYSTEM MESSAGE
# ==============================

system_message = {
    "role": "system",
    "content": (
        "You are MANU, a personal AI assistant. "
        "Be concise for simple questions and detailed only when necessary. "
        "Do not repeat the user's question. "
        "Avoid unnecessary introductions, excessive emojis, and long explanations. "
        "Give clear, direct and useful answers."
    )
}


# ==============================
# LOAD MEMORY
# ==============================

memory = load_memory()

messages = [system_message]

messages.extend(memory)


# ==============================
# START MANU
# ==============================

print("================================")
print("          MANU V0.3")
print("     Local Personal AI Agent")
print("================================")
print("Commands:")
print("/clear  - clear conversation")
print("/think  - switch to deep reasoning mode")
print("/fast   - switch to fast mode")
print("/exit   - exit MANU")
print()


# ==============================
# MAIN LOOP
# ==============================

while True:

    message = input("You: ").strip()

    if not message:
        continue


    # ==============================
    # EXIT
    # ==============================

    if message.lower() == "/exit":

        save_memory(messages[1:])

        print("MANU: Goodbye!")
        break


    # ==============================
    # CLEAR MEMORY
    # ==============================

    if message.lower() == "/clear":

        messages = [system_message]

        save_memory([])

        print("MANU: Conversation memory cleared.")
        print()

        continue


    # ==============================
    # THINKING MODE
    # ==============================

    if message.lower() == "/think":

        current_model = THINK_MODEL
        thinking_enabled = True

        print("MANU: Deep reasoning mode enabled.")
        print()

        continue


    # ==============================
    # FAST MODE
    # ==============================

    if message.lower() == "/fast":

        current_model = FAST_MODEL
        thinking_enabled = False

        print("MANU: Fast mode enabled.")
        print()

        continue


    # ==============================
    # ADD USER MESSAGE
    # ==============================

    messages.append({
        "role": "user",
        "content": message
    })


    # ==============================
    # OLLAMA REQUEST
    # ==============================

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


        print(
            f"MANU ({current_model}): ",
            end="",
            flush=True
        )


        # ==============================
        # STREAM RESPONSE
        # ==============================

        for line in response.iter_lines():

            if not line:
                continue

            chunk = json.loads(line)


            if chunk.get("done"):

                final_stats = chunk

                break


            content = chunk.get(
                "message",
                {}
            ).get(
                "content",
                ""
            )


            if content:

                print(
                    content,
                    end="",
                    flush=True
                )

                assistant_response += content


        print()


        # ==============================
        # SAVE ASSISTANT RESPONSE
        # ==============================

        messages.append({
            "role": "assistant",
            "content": assistant_response
        })


        # ==============================
        # SAVE MEMORY
        # ==============================

        save_memory(messages[1:])


        # ==============================
        # PERFORMANCE INFORMATION
        # ==============================

        if final_stats:

            total = (
                final_stats.get(
                    "total_duration",
                    0
                ) / 1_000_000_000
            )

            load = (
                final_stats.get(
                    "load_duration",
                    0
                ) / 1_000_000_000
            )

            prompt = (
                final_stats.get(
                    "prompt_eval_duration",
                    0
                ) / 1_000_000_000
            )

            generation = (
                final_stats.get(
                    "eval_duration",
                    0
                ) / 1_000_000_000
            )

            tokens = final_stats.get(
                "eval_count",
                0
            )


            print(
                f"[Total: {total:.2f}s | "
                f"Load: {load:.2f}s | "
                f"Prompt: {prompt:.2f}s | "
                f"Generation: {generation:.2f}s | "
                f"Tokens: {tokens}]"
            )


        print()


    # ==============================
    # CONNECTION ERROR
    # ==============================

    except requests.exceptions.RequestException as e:

        print(
            "\nMANU: Could not connect to Ollama."
        )

        print(
            f"Error: {e}"
        )

        print()


        # Remove failed user message

        messages.pop()


    # ==============================
    # JSON ERROR
    # ==============================

    except json.JSONDecodeError:

        print(
            "\nMANU: Could not understand Ollama's response."
        )

        print()


        # Remove failed user message

        messages.pop()