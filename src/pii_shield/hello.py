"""
Hello World module for PII Shield.

This module provides simple greeting functions to demonstrate
the package structure and usage.
"""


def get_greeting(name: str = "World") -> str:
    """
    Generate a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.

    Examples:
        >>> get_greeting()
        'Hello, World!'
        >>> get_greeting("Python")
        'Hello, Python!'
    """
    return f"Hello, {name}!"


def greet(name: str = "World") -> None:
    """
    Print a greeting message to the console.

    Args:
        name: The name to greet. Defaults to "World".

    Examples:
        >>> greet()
        Hello, World!
        >>> greet("PII Shield")
        Hello, PII Shield!
    """
    print(get_greeting(name))


if __name__ == "__main__":
    # Simple demonstration when run directly
    greet()
    greet("PII Shield")
    print(f"\nThis is a reusable module from the pii-shield package (v{__package__})")
