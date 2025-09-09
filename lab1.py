def iterative_multiply(x1, x2):
    """
    Multiplies two integers using an iterative approach (repeated addition).
    Handles negative numbers.
    """
    negative = False
    if x1 < 0 and x2 < 0:
        x1, x2 = -x1, -x2
    elif x1 < 0:
        x1 = -x1
        negative = True
    elif x2 < 0:
        x2 = -x2
        negative = True

    result = 0
    for _ in range(x2):
        result += x1

    return -result if negative else result


def recursive_multiply(x1, x2):
    """
    Multiplies two integers using recursion (primitive recursion idea).
    Handles negative numbers.
    """
    # Base case
    if x1 == 0 or x2 == 0:
        return 0

    # Handle negatives
    if x1 < 0 and x2 < 0:
        return recursive_multiply(-x1, -x2)
    elif x1 < 0:
        return -recursive_multiply(-x1, x2)
    elif x2 < 0:
        return -recursive_multiply(x1, -x2)

    # Recursive step: x1 * x2 = x1 + (x1 * (x2 - 1))
    return x1 + recursive_multiply(x1, x2 - 1)


def main():
    print("=== Laboratory Work No. 1: Recursive Functions ===")
    print("Task: Multiplication using iteration and recursion")
    print("=" * 50)

    try:
        x1 = int(input("Enter the first number (x1): "))
        x2 = int(input("Enter the second number (x2): "))

        iterative_result = iterative_multiply(x1, x2)
        recursive_result = recursive_multiply(x1, x2)

        print("\nResults:")
        print(f"Iterative multiplication: {x1} * {x2} = {iterative_result}")
        print(f"Recursive multiplication: {x1} * {x2} = {recursive_result}")
        print(f"Built-in multiplication:   {x1} * {x2} = {x1 * x2}")

        if iterative_result == recursive_result == x1 * x2:
            print("\n✓ All methods produced the same result!")
        else:
            print("\n✗ Results don't match!")

    except ValueError:
        print("Error: Please enter valid integers!")


if __name__ == "__main__":
    main()
