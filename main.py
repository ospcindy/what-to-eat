"""
Sample application demonstrating module imports from different directories.

This shows how to import and use modules from:
- src/ - Main application classes and logic
- lib/ - Library utilities (wrappers around external libraries)
- utils/ - Utility functions
"""

from src.sample_class import Calculator
from utils.sample_utils import format_number, greet


def main() -> None:
    """Run the sample application."""
    # Example 1: Using utility functions
    print("=== Example 1: Utility Functions ===")
    message = greet("World")
    print(message)

    # Example 2: Using a class from src/
    print("=== Example 2: Using Calculator Class ===")
    calc = Calculator()
    result = calc.add(10, 5)
    print(f"10 + 5 = {result}")

    result = calc.multiply(4, 2.5)
    formatted = format_number(result)
    print(f"4 ? 2.5 = {formatted}")

    result = calc.divide(100, 3)
    formatted = format_number(result, decimals=3)
    print(f"100 繩 3 = {formatted}")

    print("??Sample application completed!")


if __name__ == "__main__":
    main()