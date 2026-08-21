def calculate(a, b, operation):
    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            return "Cannot divide by zero."
        return a / b

    else:
        return "Unknown operation."


if __name__ == "__main__":

    print("MANU Calculator")

    print("10 + 5 =", calculate(10, 5, "add"))
    print("10 - 5 =", calculate(10, 5, "subtract"))
    print("10 × 5 =", calculate(10, 5, "multiply"))
    print("10 ÷ 5 =", calculate(10, 5, "divide"))