# ==========================================
# MANU V0.9 SAFETY LAYER
# ==========================================

# Tools MANU is allowed to execute
ALLOWED_TOOLS = {
    "calculator",
    "system_info",
    "list_files",
    "read_file",
    "write_file",
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
}


def is_tool_allowed(tool_name):
    """
    Check whether MANU is allowed to execute a tool.
    """

    return tool_name in ALLOWED_TOOLS


def validate_tool_call(tool_name, arguments):
    """
    Validate a tool call before execution.
    """

    # Check tool permission

    if not is_tool_allowed(tool_name):

        return {
            "allowed": False,
            "error": f"Tool '{tool_name}' is not allowed."
        }


    # Arguments must be a dictionary

    if not isinstance(arguments, dict):

        return {
            "allowed": False,
            "error": "Tool arguments must be a dictionary."
        }


    # ======================================
    # FILE SAFETY
    # ======================================

    if tool_name in {
        "read_file",
        "write_file"
    }:

        filename = arguments.get(
            "filename"
        )

        if not filename:

            return {
                "allowed": False,
                "error": "Filename is required."
            }


        # Block absolute paths

        if filename.startswith(
            ("/", "\\")
        ):

            return {
                "allowed": False,
                "error": "Absolute file paths are not allowed."
            }


        # Block Windows drive paths

        if ":" in filename:

            return {
                "allowed": False,
                "error": "Drive paths are not allowed."
            }


        # Block parent-directory traversal

        if ".." in filename.replace(
            "\\",
            "/"
        ).split("/"):

            return {
                "allowed": False,
                "error": "Parent-directory traversal is not allowed."
            }


    # ======================================
    # WRITE FILE SAFETY
    # ======================================

    if tool_name == "write_file":

        content = arguments.get(
            "content"
        )

        if content is None:

            return {
                "allowed": False,
                "error": "File content is required."
            }


    # ======================================
    # CALCULATOR SAFETY
    # ======================================

    if tool_name == "calculator":

        expression = arguments.get(
            "expression"
        )

        if not expression:

            return {
                "allowed": False,
                "error": "Calculator expression is required."
            }


    return {
        "allowed": True,
        "error": None
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Safety Layer")
    print("=================")

    tests = [

        (
            "calculator",
            {
                "expression": "25 * 25"
            }
        ),

        (
            "read_file",
            {
                "filename": "test.txt"
            }
        ),

        (
            "read_file",
            {
                "filename": "../secret.txt"
            }
        ),

        (
            "unknown_tool",
            {}
        ),

    ]


    for tool, arguments in tests:

        result = validate_tool_call(
            tool,
            arguments
        )

        print()
        print(
            f"Tool: {tool}"
        )

        print(
            f"Arguments: {arguments}"
        )

        print(
            f"Validation: {result}"
        )