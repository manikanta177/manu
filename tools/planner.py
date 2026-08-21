# ==========================================
# MANU V0.7 PLANNER
# ==========================================

ALLOWED_TOOLS = {
    "calculator",
    "system_info",
    "list_files",
    "read_file",
    "write_file"
}


def create_plan(user_request):

    return {
        "goal": user_request,
        "steps": []
    }


def validate_plan(plan):

    if not isinstance(plan, dict):
        return False

    if "steps" not in plan:
        return False

    if not isinstance(plan["steps"], list):
        return False

    for step in plan["steps"]:

        if not isinstance(step, dict):
            return False

        tool = step.get("tool")

        if tool not in ALLOWED_TOOLS:
            return False

        arguments = step.get("arguments")

        if not isinstance(arguments, dict):
            return False

    return True


def print_plan(plan):

    print()
    print("MANU Plan")
    print("=========")

    print(
        f"Goal: {plan.get('goal', '')}"
    )

    for number, step in enumerate(
        plan.get("steps", []),
        start=1
    ):

        print(
            f"{number}. "
            f"{step.get('tool')} "
            f"{step.get('arguments')}"
        )

    print()


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Planner")
    print("============")

    plan = create_plan(
        "Create a note"
    )

    plan["steps"] = [
        {
            "tool": "write_file",
            "arguments": {
                "filename": "note.txt",
                "content": "Hello from MANU V0.7"
            }
        }
    ]

    print_plan(plan)

    if validate_plan(plan):

        print(
            "Plan validation: PASSED"
        )

    else:

        print(
            "Plan validation: FAILED"
        )