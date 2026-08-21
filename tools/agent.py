# ==========================================
# MANU V0.9 AGENT LOOP + SAFETY
# ==========================================

from safety import validate_tool_call


MAX_STEPS = 5


def execute_agent_plan(plan, route_tool):

    results = []

    steps = plan.get("steps", [])

    if not steps:
        return results

    if len(steps) > MAX_STEPS:

        return [{
            "error": "Plan exceeds maximum allowed steps."
        }]

    for number, step in enumerate(
        steps,
        start=1
    ):

        tool = step.get(
            "tool"
        )

        arguments = step.get(
            "arguments",
            {}
        )

        print(
            f"MANU: Agent step "
            f"{number}/{len(steps)} → {tool}"
        )


        # ======================================
        # SAFETY CHECK
        # ======================================

        validation = validate_tool_call(
            tool,
            arguments
        )

        if not validation["allowed"]:

            result = {
                "error": validation["error"],
                "blocked_by": "MANU Safety Layer"
            }

            print(
                f"MANU: 🛡️ Tool blocked → "
                f"{validation['error']}"
            )

            results.append({
                "step": number,
                "tool": tool,
                "arguments": arguments,
                "result": result
            })

            break


        # ======================================
        # EXECUTE TOOL
        # ======================================

        try:

            result = route_tool(
                tool,
                arguments
            )

        except Exception as e:

            result = {
                "error": str(e)
            }


        # ======================================
        # OBSERVATION
        # ======================================

        observation = {
            "step": number,
            "tool": tool,
            "arguments": arguments,
            "result": result
        }

        results.append(
            observation
        )


        print(
            f"MANU: Observation → {result}"
        )


        # ======================================
        # TOOL ERROR
        # ======================================

        if isinstance(
            result,
            dict
        ):

            if "error" in result:

                print(
                    "MANU: Tool reported an error."
                )

                break


    return results


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from tool_router import route_tool

    print("MANU Agent V0.9")
    print("================")


    # ======================================
    # SAFE TEST
    # ======================================

    safe_plan = {

        "goal": "Create and read a test file",

        "steps": [

            {
                "tool": "write_file",

                "arguments": {

                    "filename": "agent_test.txt",

                    "content": "MANU V0.9"
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


    print()
    print("TEST 1: Safe plan")
    print("------------------")


    results = execute_agent_plan(
        safe_plan,
        route_tool
    )


    for result in results:

        print(result)


    # ======================================
    # BLOCKED TEST
    # ======================================

    blocked_plan = {

        "goal": "Read a protected path",

        "steps": [

            {
                "tool": "read_file",

                "arguments": {

                    "filename": "../secret.txt"
                }
            }

        ]
    }


    print()
    print("TEST 2: Unsafe plan")
    print("-------------------")


    results = execute_agent_plan(
        blocked_plan,
        route_tool
    )


    for result in results:

        print(result)


    print()
    print("MANU V0.9 safety test complete.")