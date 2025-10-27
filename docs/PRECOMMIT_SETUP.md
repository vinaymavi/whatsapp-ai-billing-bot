# Pre-commit Hooks Setup

This project uses pre-commit hooks to automatically maintain code quality and keep dependencies synchronized.

## Quick Setup

```bash
# Run the setup script
./setup-precommit.sh
```

## Manual Setup

If you prefer to set up manually:

```bash
# Install development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files (optional, for first time)
uv run pre-commit run --all-files
```

## What the Hooks Do

### 🔄 UV Sync Requirements
- **Trigger**: When `pyproject.toml` or `uv.lock` changes
- **Action**: Automatically runs `uv pip compile pyproject.toml -o requirements.txt`
- **Purpose**: Keeps `requirements.txt` in sync with your project dependencies

### 🎨 Code Quality Hooks
- **Black**: Formats Python code consistently
- **isort**: Sorts and organizes imports
- **Standard hooks**: Fixes trailing whitespace, file endings, validates YAML/JSON

## Usage

### Automatic (Recommended)
Pre-commit hooks run automatically when you make a commit:

```bash
git add .
git commit -m "Your commit message"
# Hooks run automatically before commit
```

### Manual Execution
Run hooks manually on all files:

```bash
uv run pre-commit run --all-files
```

Run hooks on specific files:

```bash
uv run pre-commit run --files app/main.py
```

### Skip Hooks (Emergency)
If you need to commit without running hooks:

```bash
git commit --no-verify -m "Emergency commit"
```

## Requirements.txt Synchronization

The main purpose of this setup is to automatically keep `requirements.txt` synchronized with `pyproject.toml`:

1. **When you modify `pyproject.toml`** (add/remove/update dependencies)
2. **Make a git commit**
3. **Pre-commit hook automatically runs** `uv pip compile pyproject.toml -o requirements.txt`
4. **Updated `requirements.txt` is added to the commit**

### Example Workflow

```bash
# 1. Add a new dependency to pyproject.toml
echo 'requests>=2.28.0' >> pyproject.toml

# 2. Commit your changes
git add pyproject.toml
git commit -m "Add requests dependency"

# 3. Pre-commit hook automatically:
#    - Runs uv pip compile pyproject.toml -o requirements.txt
#    - Adds the updated requirements.txt to your commit
#    - Shows output: "🔄 Updating requirements.txt from pyproject.toml..."
```

## Configuration File

The configuration is in `.pre-commit-config.yaml`. Key sections:

```yaml
# UV dependency sync hook
- repo: local
  hooks:
    - id: uv-sync-requirements
      name: UV Sync Requirements
      entry: bash -c 'uv pip compile pyproject.toml -o requirements.txt'
      files: ^(pyproject\.toml|uv\.lock)$
```

## Troubleshooting

### Hook fails with "command not found: uv"
Make sure `uv` is installed and in your PATH:

```bash
# Install uv if not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv
```

### Hook runs but requirements.txt not updated
Check that you're in the project root directory and `pyproject.toml` exists.

### Disable specific hooks temporarily
```bash
# Skip the requirements sync hook
SKIP=uv-sync-requirements git commit -m "Skip sync"

# Skip all hooks
git commit --no-verify -m "Skip all hooks"
```

### Update pre-commit hooks
```bash
uv run pre-commit autoupdate
```

## VSCode Integration

If you're using VSCode, the pre-commit hooks will integrate with your git workflow in the Source Control panel. You'll see the hook output in the git commit process.

## CI/CD Integration

The updated `requirements.txt` file will be automatically included in your commits, ensuring your Docker builds and deployment workflows use the correct dependencies.
