#!/bin/bash
set -e

echo "=========================================="
echo "Starting Dev Container Initialization..."
echo "=========================================="

# ==========================================
# Install Azure CLI
# ==========================================
echo ""
echo "Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify Azure CLI installation
echo "Azure CLI version:"
az --version | head -n 1

# ==========================================
# Install UV (Python package manager)
# ==========================================
echo ""
echo "Installing UV..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Add UV to PATH permanently
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# Verify UV installation
echo "UV version:"
uv --version

# ==========================================
# Initialize project with UV
# ==========================================
echo ""
echo "Syncing project dependencies with UV..."
cd /workspaces/pii-shield
uv sync

echo ""
echo "=========================================="
echo "Dev Container Initialization Complete!"
echo "=========================================="
