import requests
import json
import os

from tools.tool_router import route_tool, get_tool_instructions


OLLAMA_URL = "http://localhost:11434/api/chat"

FAST_MODEL = "qwen3:1.7b"
THINK_MODEL = "qwen3:4b"

MEMORY_FILE = "memory.json"

current_model = FAST_MODEL
thinking_enabled = False


# ==========================================
# MEMORY
# ==========================================

def load_memory():

    if os.path.exists(MEMORY_FILE):

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (json.JSONDecodeError, OSError):

            return []

    return []


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False
        )


# ==========================================
# SYSTEM
# ==========================================

system_message = {
    "role": "system",
    "content": (
        "You are MANU, a local personal AI assistant. "
        "Be clear and concise. "
        "Do not repeat the user's question. "
        "Do not use LaTeX. "
        "Do not use dollar signs for mathematics. "
        "Use normal text formatting."
    )
}


# ==========================================
# TOOL DECISION
# ==========================================

def ask_for_tool(user_message):

    messages = [
        {
            "role": "system",
            "content": get_tool_instructions()
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    data = {
        "model": current_model,
        "messages": messages,
        "think": False,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        content = (
            result
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()

        decision = json.loads(content)

        tool_name = decision.get(
            "tool",
            "none"
        )

        arguments = decision.get(
            "arguments",
            {}
        )

        allowed_tools = {
            "calculator",
            "system_info",
            "list_files",
            "read_file",
            "write_file",
            "none"
        }

        if tool_name not in allowed_tools:

            return {
                "tool": "none",
                "arguments": {}
            }

        if not isinstance(arguments, dict):

            arguments = {}

        return {
            "tool": tool_name,
            "arguments": arguments
        }

    except Exception:

        return {
            "tool": "none",
            "arguments": {}
        }


# ==========================================
# NORMAL AI RESPONSE
# ==========================================

def ask_model(messages):

    data = {
        "model": current_model,
        "messages": messages,
        "think": thinking_enabled,
        "stream": True
    }

    assistant_response = ""

    final_stats = None

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

    for line in response.iter_lines():

        if not line:
            continue

        chunk = json.loads(line)

        if chunk.get("done"):

            final_stats = chunk

            break

        content = (
            chunk
            .get("message", {})
            .get("content", "")
        )

        if content:

            print(
                content,
                end="",
                flush=True
            )

            assistant_response += content

    print()

    return assistant_response, final_stats


# ==========================================
# PERFORMANCE
# ==========================================

def show_stats(stats):

    if not stats:
        return

    total = stats.get(
        "total_duration",
        0
    ) / 1_000_000_000

    generation = stats.get(
        "eval_duration",
        0
    ) / 1_000_000_000

    tokens = stats.get(
        "eval_count",
        0
    )

    print(
        f"[Total: {total:.2f}s | "
        f"Generation: {generation:.2f}s | "
        f"Tokens: {tokens}]"
    )


# ==========================================
# START
# ==========================================

memory = load_memory()

messages = [system_message]

messages.extend(memory)


print("================================")
print("          MANU V0.6")
print("     Local Personal AI Agent")
print("================================")

print("Commands:")
print("/clear  - clear conversation")
print("/think  - deep reasoning")
print("/fast   - fast mode")
print("/exit   - exit MANU")

print()

print("Tools:")
print("- calculator")
print("- system_info")
print("- list_files")
print("- read_file")
print("- write_file")

print()


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    message = input("You: ").strip()

    if not message:
        continue


    # --------------------------------------
    # EXIT
    # --------------------------------------

    if message.lower() == "/exit":

        save_memory(messages[1:])

        print(
            "MANU: Goodbye!"
        )

        break


    # --------------------------------------
    # CLEAR
    # --------------------------------------

    if message.lower() == "/clear":

        messages = [
            system_message
        ]

        save_memory([])

        print(
            "MANU: Conversation memory cleared."
        )

        print()

        continue


    # --------------------------------------
    # THINK
    # --------------------------------------

    if message.lower() == "/think":

        current_model = THINK_MODEL

        thinking_enabled = True

        print(
            "MANU: Deep reasoning mode enabled."
        )

        print()

        continue


    # --------------------------------------
    # FAST
    # --------------------------------------

    if message.lower() == "/fast":

        current_model = FAST_MODEL

        thinking_enabled = False

        print(
            "MANU: Fast mode enabled."
        )

        print()

        continue


    # --------------------------------------
    # TOOL SELECTION
    # --------------------------------------

    decision = ask_for_tool(
        message
    )

    tool_name = decision["tool"]

    arguments = decision["arguments"]


    # --------------------------------------
    # TOOL EXECUTION
    # --------------------------------------

    if tool_name != "none":

        print(
            f"MANU: Using {tool_name}..."
        )

        result = route_tool(
            tool_name,
            arguments
        )


        # ==================================
        # CALCULATOR
        # ==================================

        if tool_name == "calculator":

            if "result" in result:

                expression = result.get(
                    "expression",
                    ""
                )

                answer = result.get(
                    "result"
                )

                output = (
                    f"{expression} = {answer}"
                )

                print(
                    f"MANU: {output}"
                )

                messages.append(
                    {
                        "role": "user",
                        "content": message
                    }
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": output
                    }
                )

                save_memory(
                    messages[1:]
                )

            else:

                print(
                    "MANU:",
                    result.get(
                        "error",
                        "Calculator error."
                    )
                )

            print()

            continue


        # ==================================
        # OTHER TOOLS
        # ==================================

        messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        messages.append(
            {
                "role": "system",
                "content": (
                    "Tool result:\n"
                    + json.dumps(
                        result,
                        ensure_ascii=False
                    )
                    + "\n\n"
                    "Answer the user's request using "
                    "the tool result. "
                    "Do not mention internal tool mechanics."
                )
            }
        )

        try:

            answer, stats = ask_model(
                messages
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            save_memory(
                messages[1:]
            )

            show_stats(stats)

        except requests.exceptions.RequestException as e:

            print(
                "MANU: Could not connect to Ollama."
            )

            print(
                f"Error: {e}"
            )

            messages.pop()
            messages.pop()

        print()

        continue


    # --------------------------------------
    # NORMAL CHAT
    # --------------------------------------

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    try:

        answer, stats = ask_model(
            messages
        )

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        save_memory(
            messages[1:]
        )

        show_stats(stats)

    except requests.exceptions.RequestException as e:

        print(
            "MANU: Could not connect to Ollama."
        )

        print(
            f"Error: {e}"
        )

        messages.pop()

    print()