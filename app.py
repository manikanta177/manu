import requests
import json
import os
import ast
import operator

from tools.system import get_system_info
from tools.files import list_files


OLLAMA_URL = "http://localhost:11434/api/chat"

FAST_MODEL = "qwen3:1.7b"
THINK_MODEL = "qwen3:4b"

MEMORY_FILE = "memory.json"

current_model = FAST_MODEL
thinking_enabled = False


# ==============================
# SAFE CALCULATOR
# ==============================

def calculate_expression(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow
        }

        def evaluate(node):

            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Only numbers are allowed.")

            if isinstance(node, ast.UnaryOp):
                value = evaluate(node.operand)

                if isinstance(node.op, ast.USub):
                    return -value

                if isinstance(node.op, ast.UAdd):
                    return value

                raise ValueError("Unsupported operation.")

            if isinstance(node, ast.BinOp):

                left = evaluate(node.left)
                right = evaluate(node.right)

                operation = allowed_operators.get(type(node.op))

                if operation is None:
                    raise ValueError("Unsupported operation.")

                if isinstance(node.op, ast.Div) and right == 0:
                    raise ValueError("Cannot divide by zero.")

                return operation(left, right)

            raise ValueError("Invalid expression.")

        return evaluate(tree)

    except Exception as e:
        return f"Calculator error: {e}"


# ==============================
# MEMORY FUNCTIONS
# ==============================

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
# DISPLAY
# ==============================

print("================================")
print("          MANU V0.4")
print("     Local Personal AI Agent")
print("================================")

print("Commands:")
print("/calc <expression> - calculator")
print("/system            - system information")
print("/files             - list MANU folder")
print("/files <folder>    - list specific folder")
print("/clear             - clear conversation")
print("/think             - switch to deep reasoning mode")
print("/fast              - switch to fast mode")
print("/exit              - exit MANU")
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

        print(
            "MANU: Conversation memory cleared."
        )

        print()

        continue


    # ==============================
    # THINKING MODE
    # ==============================

    if message.lower() == "/think":

        current_model = THINK_MODEL

        thinking_enabled = True

        print(
            "MANU: Deep reasoning mode enabled."
        )

        print()

        continue


    # ==============================
    # FAST MODE
    # ==============================

    if message.lower() == "/fast":

        current_model = FAST_MODEL

        thinking_enabled = False

        print(
            "MANU: Fast mode enabled."
        )

        print()

        continue


    # ==============================
    # CALCULATOR TOOL
    # ==============================

    if message.lower().startswith("/calc"):

        expression = message[5:].strip()

        if not expression:

            print(
                "MANU: Usage: /calc 25 * 40"
            )

            print()

            continue

        result = calculate_expression(
            expression
        )

        print(
            f"MANU Calculator: {result}"
        )

        print()

        continue


    # ==============================
    # SYSTEM INFORMATION TOOL
    # ==============================

    if message.lower() == "/system":

        print(
            "MANU System Information"
        )

        print(
            "========================"
        )

        system_info = get_system_info()

        for key, value in system_info.items():

            print(
                f"{key}: {value}"
            )

        print()

        continue


    # ==============================
    # FILE TOOL
    # ==============================

    if message.lower().startswith("/files"):

        folder = message[6:].strip()

        if not folder:
            folder = "."

        print(
            "MANU File Explorer"
        )

        print(
            "=================="
        )

        files = list_files(folder)

        for item in files:

            print(item)

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

        save_memory(
            messages[1:]
        )


        # ==============================
        # PERFORMANCE
        # ==============================

        if final_stats:

            total = (
                final_stats.get(
                    "total_duration",
                    0
                )
                / 1_000_000_000
            )

            load = (
                final_stats.get(
                    "load_duration",
                    0
                )
                / 1_000_000_000
            )

            prompt = (
                final_stats.get(
                    "prompt_eval_duration",
                    0
                )
                / 1_000_000_000
            )

            generation = (
                final_stats.get(
                    "eval_duration",
                    0
                )
                / 1_000_000_000
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


        messages.pop()


    # ==============================
    # JSON ERROR
    # ==============================

    except json.JSONDecodeError:

        print(
            "\nMANU: Could not understand Ollama's response."
        )

        print()


        messages.pop()