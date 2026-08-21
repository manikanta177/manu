# ==========================================
# MANU V1.0 TOOL ROUTER
# ==========================================

from tools.calculator import calculate
from tools.system import get_system_info
from tools.files import list_files
from tools.file_actions import read_file, write_file

from tools.task_manager import (
    add_task,
    list_tasks,
    complete_task,
    delete_task
)


# ==========================================
# TOOL ROUTER
# ==========================================

def route_tool(tool_name, arguments):

    # --------------------------------------
    # CALCULATOR
    # --------------------------------------

    if tool_name == "calculator":

        return calculate(
            arguments.get("expression", "")
        )


    # --------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------

    if tool_name == "system_info":

        return get_system_info()


    # --------------------------------------
    # LIST FILES
    # --------------------------------------

    if tool_name == "list_files":

        return list_files()


    # --------------------------------------
    # READ FILE
    # --------------------------------------

    if tool_name == "read_file":

        return read_file(
            arguments.get("filename", "")
        )


    # --------------------------------------
    # WRITE FILE
    # --------------------------------------

    if tool_name == "write_file":

        return write_file(
            arguments.get("filename", ""),
            arguments.get("content", "")
        )


    # --------------------------------------
    # ADD TASK
    # --------------------------------------

    if tool_name == "add_task":

        return add_task(
            arguments.get("title", "")
        )


    # --------------------------------------
    # LIST TASKS
    # --------------------------------------

    if tool_name == "list_tasks":

        return list_tasks()


    # --------------------------------------
    # COMPLETE TASK
    # --------------------------------------

    if tool_name == "complete_task":

        task_id = arguments.get("task_id")

        return complete_task(
            int(task_id)
        )


    # --------------------------------------
    # DELETE TASK
    # --------------------------------------

    if tool_name == "delete_task":

        task_id = arguments.get("task_id")

        return delete_task(
            int(task_id)
        )


    # --------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------

    return {
        "error": f"Unknown tool: {tool_name}"
    }


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
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Tool Router V1.0")
    print("=====================")

    print()
    print("Available tools:")

    for tool in AVAILABLE_TOOLS:

        print(
            f"- {tool}"
        )


    print()
    print("Testing calculator...")

    print(
        route_tool(
            "calculator",
            {
                "expression": "25 * 25"
            }
        )
    )


    print()
    print("Testing add_task...")

    print(
        route_tool(
            "add_task",
            {
                "title": "Test MANU V1 task"
            }
        )
    )


    print()
    print("Testing list_tasks...")

    print(
        route_tool(
            "list_tasks",
            {}
        )
    )