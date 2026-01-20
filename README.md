Protect Your PII with Presidio

A Python package for protecting Personally Identifiable Information (PII).

## Features

- 🚀 Built with modern Python packaging using `uv` - the fast Python package manager
- 📦 Reusable package structure for easy integration into other applications
- 🧪 Complete test suite with pytest
- 📚 Well-documented API with examples

## Prerequisites

- Linux/Ubuntu system (or other Unix-like OS)
- Python 3.9 or higher
- curl (for installing uv)

## Quick Start

### 1. Install uv

Run the installation script to install `uv` on your system:

```bash
chmod +x install_uv.sh
./install_uv.sh
```

After installation, restart your shell or run:
```bash
source ~/.bashrc  # or ~/.zshrc for zsh users
```

### 2. Install Project Dependencies

```bash
# Sync dependencies (creates virtual environment automatically)
uv sync

# Or install with dev dependencies
uv sync --all-extras
```

### 3. Run the Hello World Example

```bash
# Run the example using uv
uv run python examples/hello_world.py

# Or activate the virtual environment and run directly
source .venv/bin/activate
python examples/hello_world.py
```

## Usage

### As a Library

You can import and use `pii-shield` in your own Python applications:

```python
from pii_shield import greet, get_greeting, __version__

# Print a greeting
greet("World")  # Output: Hello, World!

# Get a greeting string
message = get_greeting("Python")
print(message)  # Output: Hello, Python!

# Check version
print(__version__)  # Output: 0.1.0
```

### Running Tests

```bash
# Run tests with uv
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/pii_shield --cov-report=term-missing
```

### Code Quality

```bash
# Run linter
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check --fix src/
```

## Project Structure

```
pii-shield/
├── src/
│   └── pii_shield/          # Main package source code
│       ├── __init__.py      # Package initialization
│       └── hello.py         # Hello world module
├── examples/
│   └── hello_world.py       # Example usage
├── tests/
│   └── test_hello.py        # Test suite
├── pyproject.toml           # Project configuration (uv-compatible)
├── install_uv.sh            # uv installation script
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── LICENSE                  # MIT License
```

## Development

### Setting Up Development Environment

```bash
# Install uv (if not already installed)
./install_uv.sh

# Install all dependencies including dev dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate
```

### Common Commands

```bash
# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv sync

# Run Python scripts
uv run python <script.py>

# Run tests
uv run pytest

# Run linter
uv run ruff check src/
```

## About uv

`uv` is a fast Python package installer and resolver written in Rust. It's designed to be a drop-in replacement for pip and pip-tools, but significantly faster.

### Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 Built-in virtual environment management
- 📦 Modern dependency resolution
- 🎯 Compatible with existing Python packaging standards
- 🛠️ Single tool for package management

### Learn More

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.