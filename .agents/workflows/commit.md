---
description: Guidelines for committing code to the repository.
---

# Workflow: Commit Strategy

We follow the **Conventional Commits** specification for clear and automated changelogs.

### Format
`<type>(<scope>): <description>`

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

### Examples
- `feat(auth): add login functionality`
- `fix(api): resolve timeout issue in data fetcher`
- `docs: update README with API endpoints`

### Pre-commit Hooks
Ensure dependencies are clean before committing:
```bash
git add .
# Hooks will run automatically if configured
git commit -m "..."
```
