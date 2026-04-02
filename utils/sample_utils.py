"""Sample utility functions demonstrating module organization."""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with specified decimal places."""
    return f"{value:.{decimals}f}"