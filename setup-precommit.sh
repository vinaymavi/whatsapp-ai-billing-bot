#!/bin/bash

# Script to set up pre-commit hooks for the WhatsApp AI Billing Bot project

echo "🔧 Setting up pre-commit hooks..."

# Check if we're in a virtual environment or have uv available
if command -v uv &> /dev/null; then
    echo "📦 Installing development dependencies with uv..."
    uv sync --extra dev
    UV_PYTHON=$(uv run python -c "import sys; print(sys.executable)")
    echo "🐍 Using Python from: $UV_PYTHON"

    echo "⚙️  Installing pre-commit hooks..."
    uv run pre-commit install

    echo "🧪 Running pre-commit on all files (first time)..."
    uv run pre-commit run --all-files

elif [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "📦 Installing development dependencies with pip..."
    pip install -e ".[dev]"

    echo "⚙️  Installing pre-commit hooks..."
    pre-commit install

    echo "🧪 Running pre-commit on all files (first time)..."
    pre-commit run --all-files

else
    echo "❌ Error: Please activate your virtual environment or use uv"
    echo "   For uv: Just run this script (uv will handle the environment)"
    echo "   For venv: source .venv/bin/activate && ./setup-precommit.sh"
    exit 1
fi

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "📋 The following hooks are now active:"
echo "   • UV Sync Requirements - Updates requirements.txt when pyproject.toml changes"
echo "   • Black - Python code formatting"
echo "   • isort - Import sorting"
echo "   • Standard hooks - Trailing whitespace, file endings, YAML/JSON validation"
echo ""
echo "🎯 Usage:"
echo "   • Hooks run automatically on git commit"
echo "   • To run manually: uv run pre-commit run --all-files"
echo "   • To skip hooks: git commit --no-verify"
