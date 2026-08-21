# ==========================================
# MANU V0.8 AGENT LOOP
# ==========================================

MAX_STEPS = 5


def execute_agent_plan(plan, route_tool):
    """
    Execute a validated MANU plan step by step.
    Observe every tool result.
    Stop safely if a tool fails.
    """

    results = []

    steps = plan.get("steps", [])

    if not steps:
        return results

    if len(steps) > MAX_STEPS:
        return [
            {
                "error": "Plan exceeds maximum allowed steps."
            }
        ]

    for number, step in enumerate(steps, start=1):

        tool = step.get("tool")
        arguments = step.get("arguments", {})

        print(
            f"MANU: Agent step "
            f"{number}/{len(steps)} → {tool}"
        )

        try:

            result = route_tool(
                tool,
                arguments
            )

        except Exception as e:

            result = {
                "error": str(e)
            }

        observation = {
            "step": number,
            "tool": tool,
            "arguments": arguments,
            "result": result
        }

        results.append(observation)

        print(
            f"MANU: Observation → {result}"
        )

        # Stop safely if a tool reports an error

        if isinstance(result, dict):

            if "error" in result:

                print(
                    "MANU: Agent stopped because "
                    "the tool reported an error."
                )

                break

    return results


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    # When running this file directly,
    # Python starts inside the tools directory.
    from tool_router import route_tool

    print("MANU Agent")
    print("===========")

    test_plan = {
        "goal": "Create and read a test file",

        "steps": [
            {
                "tool": "write_file",
                "arguments": {
                    "filename": "agent_test.txt",
                    "content": "MANU V0.8"
                }
            },
            {
                "tool": "read_file",
                "arguments": {
                    "filename": "agent_test.txt"
                }
            }
        ]
    }

    results = execute_agent_plan(
        test_plan,
        route_tool
    )

    print()
    print("Agent execution complete.")
    print()
    print("Results:")

    for result in results:
        print(result)