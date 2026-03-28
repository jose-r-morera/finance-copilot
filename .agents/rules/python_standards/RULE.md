---
name: python_standards
description: Strict coding standards for Python development (Ruff, Mypy, PEP 8).
---

# Python Standards Rule

This rule defines the coding standards for all Python code in this project.

## Standards
- **Language**: Python 3.11+.
- **Formatting**: Use `ruff format`. Follow PEP 8 guidelines.
- **Linting**: Use `ruff check`. Auto-fix is encouraged.
- **Typing**: Mandatory type hints for all function signatures. Use `mypy` for verification.
- **Environment**: Always use the project's local virtual environment (`.venv`) for all Python commands (tools, scripts, servers).
- **Documentation**: Google-style docstrings for all public modules, classes, and methods.
