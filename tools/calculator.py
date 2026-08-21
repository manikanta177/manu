import ast
import operator


def calculate(expression):

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow
        }

        def evaluate(node):

            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):

                if isinstance(node.value, (int, float)):
                    return node.value

                raise ValueError(
                    "Only numbers are allowed."
                )

            if isinstance(node, ast.UnaryOp):

                value = evaluate(node.operand)

                if isinstance(node.op, ast.USub):
                    return -value

                if isinstance(node.op, ast.UAdd):
                    return value

                raise ValueError(
                    "Unsupported operation."
                )

            if isinstance(node, ast.BinOp):

                left = evaluate(node.left)
                right = evaluate(node.right)

                operation = allowed_operators.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError(
                        "Unsupported operation."
                    )

                if (
                    isinstance(node.op, ast.Div)
                    and right == 0
                ):
                    raise ValueError(
                        "Cannot divide by zero."
                    )

                return operation(
                    left,
                    right
                )

            raise ValueError(
                "Invalid expression."
            )

        result = evaluate(tree)

        # Convert 625.0 → 625
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return {
            "expression": expression,
            "result": result
        }

    except Exception as e:

        return {
            "error": f"Calculator error: {e}"
        }


if __name__ == "__main__":

    print("MANU Calculator")
    print("================")

    tests = [
        "10 + 5",
        "10 - 5",
        "10 * 5",
        "10 / 5",
        "25 * 25",
        "100 / 4"
    ]

    for expression in tests:

        result = calculate(expression)

        print(
            f"{expression} = "
            f"{result}"
        )