"""
Tests for the hello module.
"""

import pytest
from pii_shield.hello import get_greeting, greet


def test_get_greeting_default():
    """Test get_greeting with default parameter."""
    result = get_greeting()
    assert result == "Hello, World!"


def test_get_greeting_custom_name():
    """Test get_greeting with custom name."""
    result = get_greeting("Python")
    assert result == "Hello, Python!"


def test_get_greeting_empty_string():
    """Test get_greeting with empty string."""
    result = get_greeting("")
    assert result == "Hello, !"


def test_greet_output(capsys):
    """Test greet function output."""
    greet()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"


def test_greet_custom_name_output(capsys):
    """Test greet function with custom name."""
    greet("PII Shield")
    captured = capsys.readouterr()
    assert captured.out == "Hello, PII Shield!\n"
