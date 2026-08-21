# ==========================================
# MANU V1.0 TASK-AWARE PLANNER
# ==========================================

import json


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

        if not isinstance(
            step["arguments"],
            dict
        ):

            return False

    return True


# ==========================================
# SIMPLE RULE-BASED PLANNER
# ==========================================

def create_plan(user_message):

    message = user_message.lower().strip()


    # --------------------------------------
    # CALCULATOR
    # --------------------------------------

    calculation_words = [
        "calculate",
        "what is",
        "compute",
        "solve"
    ]

    if any(
        word in message
        for word in calculation_words
    ):

        expression = (
            message
            .replace("calculate", "")
            .replace("compute", "")
            .replace("solve", "")
            .strip()
        )

        if expression.startswith("what is"):

            expression = expression[7:].strip()

        return [
            {
                "tool": "calculator",
                "arguments": {
                    "expression": expression
                }
            }
        ]


    # --------------------------------------
    # ADD TASK
    # --------------------------------------

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


    # --------------------------------------
    # LIST TASKS
    # --------------------------------------

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


    # --------------------------------------
    # COMPLETE TASK
    # --------------------------------------

    if (
        "complete task" in message
        or "finish task" in message
        or "mark task" in message
    ):

        import re

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


    # --------------------------------------
    # DELETE TASK
    # --------------------------------------

    if (
        "delete task" in message
        or "remove task" in message
    ):

        import re

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


    # --------------------------------------
    # FILE CREATION
    # --------------------------------------

    if (
        "create a file" in message
        or "create file" in message
        or "write a file" in message
    ):

        import re

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


    # --------------------------------------
    # FILE READING
    # --------------------------------------

    if (
        message.startswith("read ")
        or "read file" in message
    ):

        filename = ""

        if message.startswith("read "):

            filename = user_message[5:].strip()

        else:

            import re

            match = re.search(
                r"read file\s+(.+)",
                user_message,
                re.IGNORECASE
            )

            if match:

                filename = match.group(1).strip()

        if filename:

            return [
                {
                    "tool": "read_file",
                    "arguments": {
                        "filename": filename
                    }
                }
            ]


    # --------------------------------------
    # NO TOOL REQUIRED
    # --------------------------------------

    return []


# ==========================================
# PLAN DISPLAY
# ==========================================

def print_plan(plan):

    print()
    print("MANU Plan")
    print("=========")

    if not plan:

        print("No tools required.")

        return


    for index, step in enumerate(
        plan,
        start=1
    ):

        print(
            f"{index}. "
            f"{step['tool']} "
            f"{step['arguments']}"
        )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Planner V1.0")
    print("=================")


    tests = [

        "calculate 25 * 25",

        "Add a task called Finish MANU V1",

        "Show me my tasks",

        "Complete task 2",

        "Delete task 3",

        "Create a file called test.txt with the content Hello MANU",

        "Read test.txt"
    ]


    for test in tests:

        print()
        print(
            f"Goal: {test}"
        )

        plan = create_plan(
            test
        )

        print_plan(
            plan
        )

        print(
            "Plan validation:",
            "PASSED"
            if validate_plan(plan)
            else "FAILED"
        )