from pathlib import Path

path = Path("tools/tool_router.py")
content = path.read_text(encoding="utf-8")

if "from tools.memory import remember, recall, list_facts, forget" not in content:
    content = content.replace(
        "from tools.memory import remember, recall, list_facts",
        "from tools.memory import remember, recall, list_facts, forget"
    )

marker = "    # --------------------------------------\n    # UNKNOWN TOOL"

block = """    # --------------------------------------
    # FORGET
    # --------------------------------------

    if tool_name == "forget":

        key = arguments.get(
            "key",
            ""
        )

        return forget(
            key
        )


"""

if 'if tool_name == "forget":' not in content:
    if marker not in content:
        raise SystemExit("UNKNOWN TOOL marker not found")

    content = content.replace(
        marker,
        block + marker,
        1
    )

path.write_text(content, encoding="utf-8")

print("FORGET ROUTER ADDED SUCCESSFULLY.")
