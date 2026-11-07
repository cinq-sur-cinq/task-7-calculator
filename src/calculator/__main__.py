"""Command-line entry point for the calculator."""

from .evaluator import evaluate


def main() -> None:
    previous = None
    while True:
        try:
            expression = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not expression.strip():
            continue

        try:
            result = evaluate(expression, previous)
        except ValueError as error:
            print(f"Error: {error}")
        else:
            print(result)
            previous = result


if __name__ == "__main__":
    main()
