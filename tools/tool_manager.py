from calculator import calculate
from system import get_system_info
from files import list_files


def calculator_tool(a, b, operation):
    return calculate(a, b, operation)


def system_info_tool():
    return get_system_info()


def file_list_tool(folder="."):
    return list_files(folder)


TOOLS = {
    "calculator": calculator_tool,
    "system_info": system_info_tool,
    "list_files": file_list_tool
}


def get_tool(tool_name):
    return TOOLS.get(tool_name)


def list_tools():
    return list(TOOLS.keys())


if __name__ == "__main__":

    print("MANU Tool Manager")
    print("=================")

    print("Available tools:")

    for tool in list_tools():
        print("-", tool)