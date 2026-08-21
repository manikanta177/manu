try:
    from tools.calculator import calculate
    from tools.system import get_system_info
    from tools.files import list_files
    from tools.file_actions import (
        read_file,
        write_file
    )
except ModuleNotFoundError:
    from calculator import calculate
    from system import get_system_info
    from files import list_files
    from file_actions import (
        read_file,
        write_file
    )


# ==========================================
# AVAILABLE TOOLS
# ==========================================

AVAILABLE_TOOLS = [
    "calculator",
    "system_info",
    "list_files",
    "read_file",
    "write_file",
    "none"
]


# ==========================================
# TOOL INSTRUCTIONS FOR QWEN
# ==========================================

def get_tool_instructions():

    return """
You are MANU's tool selection system.

Your job is to decide whether the user's request requires a tool.

You MUST return ONLY valid JSON.

Available tools:

1. calculator
Use for mathematical calculations.

Arguments:
{
    "expression": "25 * 25"
}

2. system_info
Use for information about the computer's operating system,
CPU, architecture, processor, or basic system information.

Arguments:
{}

3. list_files
Use when the user wants to see files or folders.

Arguments:
{
    "folder": "."
}

4. read_file
Use when the user asks MANU to read a text file.

Arguments:
{
    "filename": "README.md"
}

5. write_file
Use when the user asks MANU to create or write a text file.

Arguments:
{
    "filename": "notes.txt",
    "content": "Hello from MANU"
}

6. none
Use for normal conversation, explanations, coding questions,
general questions, greetings, and anything that does not require
a tool.

Arguments:
{}

IMPORTANT SAFETY RULES:

- Never invent a tool.
- Never request shell commands.
- Never request Python execution.
- Never delete files.
- Never modify files unless the user explicitly requests
  write_file.
- read_file and write_file are restricted to the MANU project.
- Return ONLY JSON.
- Do not use Markdown.
- Do not include explanations outside the JSON.

Examples:

User:
"Calculate 25 times 25"

Return:
{
    "tool": "calculator",
    "arguments": {
        "expression": "25 * 25"
    }
}

User:
"What operating system am I using?"

Return:
{
    "tool": "system_info",
    "arguments": {}
}

User:
"Show me the files in the tools folder"

Return:
{
    "tool": "list_files",
    "arguments": {
        "folder": "tools"
    }
}

User:
"Read README.md"

Return:
{
    "tool": "read_file",
    "arguments": {
        "filename": "README.md"
    }
}

User:
"Create a file called hello.txt containing Hello MANU"

Return:
{
    "tool": "write_file",
    "arguments": {
        "filename": "hello.txt",
        "content": "Hello MANU"
    }
}

User:
"Hello MANU"

Return:
{
    "tool": "none",
    "arguments": {}
}
"""


# ==========================================
# TOOL ROUTER
# ==========================================

def route_tool(tool_name, arguments=None):

    if arguments is None:
        arguments = {}


    # --------------------------------------
    # SECURITY: ALLOWLIST
    # --------------------------------------

    if tool_name not in AVAILABLE_TOOLS:

        return {
            "error": f"Unknown tool: {tool_name}"
        }


    # --------------------------------------
    # CALCULATOR
    # --------------------------------------

    if tool_name == "calculator":

        expression = arguments.get(
            "expression",
            ""
        )

        if not expression:

            return {
                "error": "No expression provided."
            }

        return calculate(expression)


    # --------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------

    if tool_name == "system_info":

        return get_system_info()


    # --------------------------------------
    # FILE LIST
    # --------------------------------------

    if tool_name == "list_files":

        folder = arguments.get(
            "folder",
            "."
        )

        return list_files(folder)


    # --------------------------------------
    # READ FILE
    # --------------------------------------

    if tool_name == "read_file":

        filename = arguments.get(
            "filename",
            ""
        )

        if not filename:

            return {
                "error": "No filename provided."
            }

        return read_file(filename)


    # --------------------------------------
    # WRITE FILE
    # --------------------------------------

    if tool_name == "write_file":

        filename = arguments.get(
            "filename",
            ""
        )

        content = arguments.get(
            "content",
            ""
        )

        if not filename:

            return {
                "error": "No filename provided."
            }

        return write_file(
            filename,
            content
        )


    # --------------------------------------
    # NONE
    # --------------------------------------

    if tool_name == "none":

        return {
            "status": "No tool required."
        }


    # --------------------------------------
    # FALLBACK
    # --------------------------------------

    return {
        "error": "Tool could not be executed."
    }


# ==========================================
# DIRECT TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Tool Router")
    print("=================")

    print("\nAvailable tools:")

    for tool in AVAILABLE_TOOLS:
        print("-", tool)

    print("\nCalculator test:")

    print(
        route_tool(
            "calculator",
            {
                "expression": "25 * 40"
            }
        )
    )

    print("\nSystem test:")

    print(
        route_tool(
            "system_info",
            {}
        )
    )

    print("\nFile list test:")

    print(
        route_tool(
            "list_files",
            {
                "folder": "."
            }
        )
    )

    print("\nRead file test:")

    print(
        route_tool(
            "read_file",
            {
                "filename": "manu_test.txt"
            }
        )
    )