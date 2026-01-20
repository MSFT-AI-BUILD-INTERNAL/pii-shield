#!/usr/bin/env python3
"""
Hello World Example for PII Shield

This example demonstrates how to use the pii-shield package
from another application.
"""

# Import from the pii_shield package
from pii_shield import greet, get_greeting, __version__


def main():
    """Main function demonstrating package usage."""
    print("=" * 50)
    print("PII Shield - Hello World Example")
    print("=" * 50)
    print()

    # Display version
    print(f"Package Version: {__version__}")
    print()

    # Example 1: Using the greet function
    print("Example 1: Using greet()")
    greet()
    print()

    # Example 2: Using greet with a custom name
    print("Example 2: Using greet() with custom name")
    greet("PII Shield User")
    print()

    # Example 3: Using get_greeting to retrieve the message
    print("Example 3: Using get_greeting() to get the message")
    message = get_greeting("Developer")
    print(f"Retrieved message: {message}")
    print()

    # Example 4: Multiple greetings
    print("Example 4: Multiple greetings")
    names = ["Alice", "Bob", "Charlie"]
    for name in names:
        greeting = get_greeting(name)
        print(f"  - {greeting}")
    print()

    print("=" * 50)
    print("Example completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
