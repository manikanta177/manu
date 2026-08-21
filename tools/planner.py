# ==========================================
# MANU V1.1 TASK-AWARE PLANNER
# ==========================================

import re


# ==========================================
# AVAILABLE TOOLS
# ==========================================

AVAILABLE_TOOLS = [
    "calculator",
    "system_info",
    "list_files",
    "read_file",
    "write_file",
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task"
]


# ==========================================
# TOOL DESCRIPTIONS
# ==========================================

TOOL_DESCRIPTIONS = {

    "calculator":
        "Perform mathematical calculations.",

    "system_info":
        "Get information about the computer.",

    "list_files":
        "List files in the MANU project.",

    "read_file":
        "Read the contents of a file.",

    "write_file":
        "Create or write a file.",

    "add_task":
        "Add a new task to the persistent task list.",

    "list_tasks":
        "Show all persistent tasks.",

    "complete_task":
        "Mark an existing task as completed using its task ID.",

    "delete_task":
        "Delete an existing task using its task ID."
}


# ==========================================
# PLAN VALIDATION
# ==========================================

def validate_plan(plan):

    if not isinstance(plan, list):
        return False

    for step in plan:

        if not isinstance(step, dict):
            return False

        if "tool" not in step:
            return False

        if "arguments" not in step:
            return False

        if step["tool"] not in AVAILABLE_TOOLS:
            return False

        if not isinstance(step["arguments"], dict):
            return False

    return True


# ==========================================
# CALCULATOR DETECTION
# ==========================================

def is_math_request(message):

    calculation_words = [
        "calculate",
        "compute",
        "solve"
    ]

    if any(
        word in message
        for word in calculation_words
    ):
        return True

    # "what is 25 * 25" should be calculator
    if "what is" in message:

        has_number = any(
            char.isdigit()
            for char in message
        )

        has_operator = any(
            operator in message
            for operator in [
                "+",
                "-",
                "*",
                "/",
                "%",
                "^"
            ]
        )

        if has_number and has_operator:
            return True

    return False


# ==========================================
# SIMPLE RULE-BASED PLANNER
# ==========================================

def create_plan(user_message):

    message = user_message.lower().strip()


    # ======================================
    # CALCULATOR
    # ======================================

    if is_math_request(message):

        expression = message

        prefixes = [
            "calculate",
            "compute",
            "solve"
        ]

        for prefix in prefixes:

            if expression.startswith(prefix):

                expression = expression[
                    len(prefix):
                ].strip()

                break

        if expression.startswith("what is"):

            expression = expression[
                len("what is"):
            ].strip()

        return [
            {
                "tool": "calculator",
                "arguments": {
                    "expression": expression
                }
            }
        ]

    # ======================================
    # REMEMBER
    # ======================================

    if (
        "remember that" in message
        or "remember my" in message
        or "remember this" in message
    ):

        text = user_message.strip()

        if "remember that" in message:

            fact = text[
                message.find("remember that") + len("remember that"):
            ].strip()

        elif "remember my" in message:

            fact = text[
                message.lower().find("remember my") + len("remember my"):
            ].strip()

        else:

            fact = text[
                message.lower().find("remember this") + len("remember this"):
            ].strip()


        if "=" in fact:

            key, value = fact.split(
                "=",
                1
            )

        elif " is " in fact:

            key, value = fact.split(
                " is ",
                1
            )

        else:

            key = "general"
            value = fact


        key = key.strip()
        value = value.strip()

        if key.lower().startswith("my "):

            key = key[3:]


        return [
            {
                "tool": "remember",
                "arguments": {
                    "key": key,
                    "value": value
                }
            }
        ]
    # ======================================
    # RECALL
    # ======================================

    if (
        message.startswith("what is my ")
        or message.startswith("what's my ")
    ):

        key = message

        if message.startswith("what is my "):

            key = message[
                len("what is my "):
            ]

        elif message.startswith("what's my "):

            key = message[
                len("what's my "):
            ]

        key = key.strip(
            " ?!."
        )

        if key:

            return [
                {
                    "tool": "recall",
                    "arguments": {
                        "key": key
                    }
                }
            ]


    if message == "who am i":

        return [
            {
                "tool": "recall",
                "arguments": {
                    "key": "name"
                }
            }
        ]

    # ADD TASK
    # ======================================

    if (
        "add a task" in message
        or "add task" in message
        or "create a task" in message
        or "new task" in message
    ):

        title = user_message

        prefixes = [
            "add a task called ",
            "add task called ",
            "add a task ",
            "add task ",
            "create a task called ",
            "create a task ",
            "new task "
        ]

        for prefix in prefixes:

            if message.startswith(prefix):

                title = user_message[
                    len(prefix):
                ].strip()

                break

        return [
            {
                "tool": "add_task",
                "arguments": {
                    "title": title
                }
            }
        ]


    # ======================================
    # LIST FACTS
    # ======================================

    if (
        "show my facts" in message
        or "show me my facts" in message
        or "what do you remember about me" in message
        or "what do you know about me" in message
        or "list my facts" in message
        or "list facts" in message
        or message == "my facts"
    ):

        return [
            {
                "tool": "list_facts",
                "arguments": {}
            }
        ]

    # ======================================
    # LIST TASKS
    # ======================================

    if (
        "show my tasks" in message
        or "show me my tasks" in message
        or "show tasks" in message
        or "list my tasks" in message
        or "list tasks" in message
        or message == "my tasks"
    ):

        return [
            {
                "tool": "list_tasks",
                "arguments": {}
            }
        ]


    # ======================================
    # COMPLETE TASK
    # ======================================

    if (
        "complete task" in message
        or "finish task" in message
        or "mark task" in message
    ):

        match = re.search(
            r"\btask\s+(\d+)\b",
            message
        )

        if match:

            task_id = int(
                match.group(1)
            )

            return [
                {
                    "tool": "complete_task",
                    "arguments": {
                        "task_id": task_id
                    }
                }
            ]


    # ======================================
    # DELETE TASK
    # ======================================

    if (
        "delete task" in message
        or "remove task" in message
    ):

        match = re.search(
            r"\btask\s+(\d+)\b",
            message
        )

        if match:

            task_id = int(
                match.group(1)
            )

            return [
                {
                    "tool": "delete_task",
                    "arguments": {
                        "task_id": task_id
                    }
                }
            ]


    # ======================================
    # FILE CREATION
    # ======================================

    if (
        "create a file" in message
        or "create file" in message
        or "write a file" in message
    ):

        filename_match = re.search(
            r"(?:file called|file named|file)\s+([^\s]+)",
            message
        )

        content_match = re.search(
            r"content\s+(.+)",
            user_message,
            re.IGNORECASE
        )

        if filename_match:

            filename = filename_match.group(1)

            content = ""

            if content_match:

                content = content_match.group(1).strip()

            return [
                {
                    "tool": "write_file",
                    "arguments": {
                        "filename": filename,
                        "content": content
                    }
                }
            ]


    # ======================================
    # FILE READING
    # ======================================

    if (
        message.startswith("read ")
        or message.startswith("open ")
    ):

        filename = ""

        prefixes = [
            "read ",
            "open "
        ]

        for prefix in prefixes:

            if message.startswith(prefix):

                filename = user_message[
                    len(prefix):
                ].strip()

                break

        if filename:

            return [
                {
                    "tool": "read_file",
                    "arguments": {
                        "filename": filename
                    }
                }
            ]


    # ======================================
    # LIST FILES
    # ======================================

    if (
        "list files" in message
        or "show files" in message
        or message == "files"
    ):

        return [
            {
                "tool": "list_files",
                "arguments": {}
            }
        ]


    # ======================================
    # SYSTEM INFORMATION
    # ======================================

    if (
        "system info" in message
        or "system information" in message
        or "computer information" in message
        or "computer specs" in message
    ):

        return [
            {
                "tool": "system_info",
                "arguments": {}
            }
        ]


    # ======================================
    # NO TOOL REQUIRED
    # ======================================

    return []


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    test_requests = [

        "calculate 25 * 25",

        "what is 25 * 25",

        "what is my name",

        "Add a task called Finish MANU V1",

        "Show me my tasks",

        "Complete task 2",

        "Delete task 3",

        "Create a file called test.txt with the content Hello MANU",

        "Read test.txt",

        "Show me my files"
    ]

    print("MANU Planner V1.1")
    print("=================")

    for request in test_requests:

        print()
        print("Goal:", request)
        print()
        print("MANU Plan")
        print("=========")

        plan = create_plan(request)

        if not plan:

            print("No tools required.")

        else:

            for index, step in enumerate(
                plan,
                start=1
            ):

                print(
                    f"{index}. "
                    f"{step['tool']} "
                    f"{step['arguments']}"
                )

        print(
            "Plan validation:",
            "PASSED"
            if validate_plan(plan)
            else "FAILED"
        )