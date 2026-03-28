---
description: Guidelines for committing code to the repository.
---

# Workflow: Commit Strategy

We follow the **Conventional Commits** specification for clear and automated changelogs.

### Format
`<type>(<scope>): <description>`

### Atomic Commits
**CRITICAL**: Every commit must be atomic. Do NOT combine unrelated changes into a single commit.
- One feature per commit.
- One logical infrastructure change per commit.
- One bug fix per commit.
- Tests and documentation for a feature should be in the same commit as the feature itself if reasonable, or in a separate follow-up commit.

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
- `feat(infra): add postgresql to docker-compose`
- `feat(db): implement company models`
- `feat(auth): add login functionality`
- `fix(api): resolve timeout issue in data fetcher`
- `docs: update README with API endpoints`

### Pre-commit Hooks
Ensure dependencies are clean before committing:
```bash
# Add ONLY the files relevant to the atomic change
git add <specific file1> <specific file2>
# Commit with a focused message
git commit -m "..."
```
