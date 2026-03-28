---
name: python_dev
description: Managing the Python environment, linting (Ruff), and type checking (Mypy) for this project.
---

# Python Development Skill

This skill provides instructions for the Antigravity developer agent to manage the Python environment and ensure code quality.

## Tools Summary
- `pip`: Package management (requirements.txt).
- `ruff`: High-speed linting and formatting.
- `mypy`: Static type checking.
- `pytest`: Running the test suite.

## Usage Guidelines
- Always use `make install-dev` to set up the environment.
- Run `make check` before every major change.
- Ensure all new functions have proper type hints and docstrings.
