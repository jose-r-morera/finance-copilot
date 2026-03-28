# Contributing to finance-copilot

Thank you for contributing! This guide explains how to set up your environment and follow our quality standards.

---

## Development Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/jose-r-morera/finance-copilot.git
cd finance-copilot

# 2. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install all dependencies + pre-commit hooks
make install-dev

# 4. Copy the environment template and fill in your keys
cp .env.example .env
$EDITOR .env

# 5. Start the backend server (no Docker required)
make dev
# or with Docker:
make up
```

---

## Branch Strategy

| Branch pattern | Purpose |
|---|---|
| `main` | Stable, always deployable |
| `dev` | Integration branch — PRs merge here first |
| `feat/<short-description>` | New features |
| `fix/<short-description>` | Bug fixes |
| `chore/<short-description>` | Tooling, config, dependencies |
| `docs/<short-description>` | Documentation only |

---

## Commit Style

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

Examples:
feat(agents): add DCF calculator tool
fix(api): handle missing ticker symbol gracefully
docs(readme): add architecture diagram
chore(deps): bump langchain to 0.2.1
```

### Types
`feat` | `fix` | `docs` | `style` | `refactor` | `test` | `chore` | `perf`

---

## Pull Request Checklist

Before opening a PR against `dev`:

- [ ] `make check` passes (lint + typecheck)
- [ ] `make test` passes with no failures
- [ ] New behaviour is covered by at least one test
- [ ] `.env.example` updated if new env vars are added
- [ ] `WORKPLAN.md` / `README.md` updated if architecture changes

---

## Code Style

- **Formatter**: `ruff format` (configured in `pyproject.toml`)
- **Linter**: `ruff check` with auto-fix
- **Type hints**: required on all public functions/methods
- **Docstrings**: Google-style on all public modules, classes, and functions
- **Line length**: 100 characters

Pre-commit hooks enforce all of the above automatically on every commit.

---

## Adding a New Dependency

1. Add it to `pyproject.toml` under `[project.dependencies]` or `[project.optional-dependencies].dev`
2. Regenerate `requirements.txt` / `requirements-dev.txt`:
   ```bash
   pip-compile pyproject.toml -o requirements.txt
   pip-compile pyproject.toml --extra dev -o requirements-dev.txt
   ```
3. Commit both files

---

## Data & Secrets Policy

- **Never** commit `.env` or any file containing real API keys
- **Never** commit raw financial data (in `data/raw/`, `data/cache/`)
- All scraping must comply with the target site's Terms of Service
- All AI-generated financial outputs must include the disclaimer: *"Not investment advice"*
