#!/bin/bash
# Installation script for uv on Linux/Ubuntu systems
# uv is a fast Python package installer and resolver written in Rust

set -e  # Exit on error

echo "========================================"
echo "Installing uv - Fast Python Package Manager"
echo "========================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This script is designed for Linux/Ubuntu systems."
    echo "Current OS: $OSTYPE"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if uv is already installed
if command -v uv &> /dev/null; then
    echo "✓ uv is already installed!"
    uv --version
    read -p "Do you want to reinstall/update uv? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping installation."
        exit 0
    fi
fi

# Install uv using the official installation script
echo "Downloading and installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
export PATH="$HOME/.cargo/bin:$PATH"

# Check if installation was successful
if command -v uv &> /dev/null; then
    echo ""
    echo "✓ uv has been successfully installed!"
    echo "Version: $(uv --version)"
    echo ""
    echo "========================================"
    echo "Next Steps:"
    echo "========================================"
    echo "1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Verify installation: uv --version"
    echo "3. Install project dependencies: uv sync"
    echo "4. Run the hello world example: uv run python examples/hello_world.py"
    echo ""
else
    echo ""
    echo "✗ Installation failed. Please check the error messages above."
    exit 1
fi
