#!/bin/bash
# Quick start script for PII Shield
# This script helps you get started with the project quickly

set -e

echo "========================================"
echo "PII Shield - Quick Start"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "Please run ./install_uv.sh first to install uv."
    echo ""
    echo "Alternatively, you can use regular Python:"
    echo "  1. pip install -e ."
    echo "  2. python examples/hello_world.py"
    exit 1
fi

echo "✓ uv is installed: $(uv --version)"
echo ""

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras
echo ""

# Run the example
echo "🚀 Running hello world example..."
echo ""
uv run python examples/hello_world.py
echo ""

# Run tests
echo "🧪 Running tests..."
echo ""
uv run pytest tests/ -v
echo ""

echo "========================================"
echo "✓ Quick start completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  - Activate virtual environment: source .venv/bin/activate"
echo "  - View the code: cat src/pii_shield/hello.py"
echo "  - Read the README: cat README.md"
echo ""
