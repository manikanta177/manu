import requests
import json
import os

from tools.tool_router import route_tool, get_tool_instructions
from tools.planner import validate_plan


# ==========================================
# CONFIGURATION
# ==========================================

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

    if not os.path.exists(MEMORY_FILE):
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []


def save_memory(memory):

    try:

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

    except OSError as e:

        print(
            f"MANU: Could not save memory: {e}"
        )


# ==========================================
# SYSTEM MESSAGE
# ==========================================

system_message = {
    "role": "system",
    "content": (
        "You are MANU, a local personal AI assistant. "
        "Be clear, direct and useful. "
        "Be concise for simple questions. "
        "Do not repeat the user's question. "
        "Do not use LaTeX or dollar signs for mathematics."
    )
}


# ==========================================
# CLEAN JSON RESPONSE
# ==========================================

def clean_json(text):

    text = text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        if lines:

            lines = lines[1:]

        if lines and lines[-1].strip() == "```":

            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


# ==========================================
# ASK QWEN
# ==========================================

def ask_ollama(messages, stream=False):

    data = {
        "model": current_model,
        "messages": messages,
        "think": thinking_enabled,
        "stream": stream
    }

    response = requests.post(
        OLLAMA_URL,
        json=data,
        stream=stream,
        timeout=300
    )

    response.raise_for_status()

    if not stream:

        return response.json()

    return response


# ==========================================
# CREATE PLAN
# ==========================================

def create_plan(user_request):

    planner_prompt = """
You are MANU's planning engine.

Convert the user's request into a JSON execution plan.

Available tools:

calculator
system_info
list_files
read_file
write_file

Rules:

1. Return ONLY valid JSON.
2. Do not use Markdown.
3. Use multiple steps when necessary.
4. Use the minimum number of steps needed.
5. Never invent tools.
6. Never delete files.
7. Never execute shell commands.
8. write_file requires explicit user intent to create/write a file.
9. Normal conversation should return an empty steps list.

Required format:

{
    "goal": "short description",
    "steps": [
        {
            "tool": "tool_name",
            "arguments": {}
        }
    ]
}

Examples:

User:
"Create hello.txt containing Hello MANU"

Response:
{
    "goal": "Create hello.txt",
    "steps": [
        {
            "tool": "write_file",
            "arguments": {
                "filename": "hello.txt",
                "content": "Hello MANU"
            }
        }
    ]
}

User:
"Create note.txt with MANU V0.7 and then read it"

Response:
{
    "goal": "Create and verify note.txt",
    "steps": [
        {
            "tool": "write_file",
            "arguments": {
                "filename": "note.txt",
                "content": "MANU V0.7"
            }
        },
        {
            "tool": "read_file",
            "arguments": {
                "filename": "note.txt"
            }
        }
    ]
}

User:
"What is Python?"

Response:
{
    "goal": "Answer the question",
    "steps": []
}
"""

    messages = [
        {
            "role": "system",
            "content": planner_prompt
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    try:

        data = ask_ollama(
            messages,
            stream=False
        )

        content = (
            data
            .get("message", {})
            .get("content", "")
        )

        content = clean_json(content)

        plan = json.loads(content)

        if not validate_plan(plan):

            return {
                "goal": user_request,
                "steps": []
            }

        return plan

    except (
        requests.exceptions.RequestException,
        json.JSONDecodeError,
        TypeError,
        ValueError
    ):

        return {
            "goal": user_request,
            "steps": []
        }


# ==========================================
# EXECUTE PLAN
# ==========================================

def execute_plan(plan):

    results = []

    steps = plan.get(
        "steps",
        []
    )

    for number, step in enumerate(
        steps,
        start=1
    ):

        tool_name = step.get(
            "tool"
        )

        arguments = step.get(
            "arguments",
            {}
        )

        print(
            f"MANU: Step {number}/{len(steps)} "
            f"→ {tool_name}"
        )

        result = route_tool(
            tool_name,
            arguments
        )

        results.append(
            {
                "step": number,
                "tool": tool_name,
                "result": result
            }
        )

        if isinstance(result, dict):

            if "error" in result:

                print(
                    f"MANU: Step {number} failed."
                )

                break

    return results


# ==========================================
# FINAL RESPONSE
# ==========================================

def generate_final_response(
    user_request,
    plan,
    results
):

    tool_results = json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are MANU.

The user asked:

{user_request}

The execution plan was:

{json.dumps(plan, indent=2, ensure_ascii=False)}

The tool results were:

{tool_results}

Give the user a clear final answer.

Rules:
- Do not mention internal architecture.
- Do not mention Qwen.
- Do not mention JSON.
- Do not repeat the user's request.
- Be concise.
"""

    messages = [
        system_message,
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = ask_ollama(
        messages,
        stream=True
    )

    assistant_response = ""
    final_stats = None

    print(
        f"MANU ({current_model}): ",
        end="",
        flush=True
    )

    for line in response.iter_lines():

        if not line:
            continue

        try:

            chunk = json.loads(line)

        except json.JSONDecodeError:

            continue

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
# NORMAL CHAT
# ==========================================

def normal_response(user_message):

    global messages

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    try:

        response = ask_ollama(
            messages,
            stream=True
        )

        assistant_response = ""
        final_stats = None

        print(
            f"MANU ({current_model}): ",
            end="",
            flush=True
        )

        for line in response.iter_lines():

            if not line:
                continue

            try:

                chunk = json.loads(line)

            except json.JSONDecodeError:

                continue

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

        messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )

        save_memory(
            messages[1:]
        )

        return final_stats

    except requests.exceptions.RequestException as e:

        print(
            "MANU: Could not connect to Ollama."
        )

        print(
            f"Error: {e}"
        )

        messages.pop()

        return None


# ==========================================
# PERFORMANCE
# ==========================================

def show_stats(stats):

    if not stats:
        return

    total = (
        stats.get(
            "total_duration",
            0
        ) / 1_000_000_000
    )

    generation = (
        stats.get(
            "eval_duration",
            0
        ) / 1_000_000_000
    )

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
# START MANU
# ==========================================

memory = load_memory()

messages = [
    system_message
]

messages.extend(
    memory
)


print("================================")
print("          MANU V0.7")
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

print("Planner: ENABLED")
print()


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    message = input(
        "You: "
    ).strip()

    if not message:
        continue


    # --------------------------------------
    # EXIT
    # --------------------------------------

    if message.lower() == "/exit":

        save_memory(
            messages[1:]
        )

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
    # CREATE PLAN
    # --------------------------------------

    print(
        "MANU: Planning..."
    )

    plan = create_plan(
        message
    )

    steps = plan.get(
        "steps",
        []
    )


    # --------------------------------------
    # NO TOOL REQUIRED
    # --------------------------------------

    if not steps:

        stats = normal_response(
            message
        )

        show_stats(
            stats
        )

        print()

        continue


    # --------------------------------------
    # SHOW PLAN
    # --------------------------------------

    print(
        f"MANU: Plan created "
        f"({len(steps)} step"
        f"{'' if len(steps) == 1 else 's'})."
    )


    # --------------------------------------
    # EXECUTE
    # --------------------------------------

    try:

        results = execute_plan(
            plan
        )

        answer, stats = generate_final_response(
            message,
            plan,
            results
        )

        # Save compact conversation memory

        messages.append(
            {
                "role": "user",
                "content": message
            }
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

        show_stats(
            stats
        )

    except requests.exceptions.RequestException as e:

        print(
            "MANU: Could not connect to Ollama."
        )

        print(
            f"Error: {e}"
        )

    except Exception as e:

        print(
            f"MANU: Task execution error: {e}"
        )

    print()