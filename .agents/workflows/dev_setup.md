---
description: Pipeline to set up the local development environment for this project.
---

# Workflow: Developer Setup

1. **Verify Python**: Ensure Python 3.11+ is installed.
2. **Setup Venv**: `python3.11 -m venv .venv && source .venv/bin/activate`.
3. **Install Deps**: `make install-dev`.
4. **Environment**: `cp .env.example .env` and update the necessary keys.
5. **Verify**: Use the `quality_check` workflow to ensure the base project is healthy.
