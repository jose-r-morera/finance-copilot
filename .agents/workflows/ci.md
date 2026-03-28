---
description: Pipeline for Continuous Integration checks.
---

# Workflow: CI Pipeline

Standard checks to be run on every pull request or push to main.

### 1. Static Analysis
Run linting and formatting checks:
```bash
make lint
make typecheck
```
For frontend specific:
```bash
cd frontend && npm run lint
```

### 2. Automated Testing
Execute the full test suite as defined in the `testing` workflow.

### 3. Build Verification
Ensure Docker images build correctly:
```bash
make build
```

### 4. Security Audit
Check for known vulnerabilities:
```bash
cd frontend && npm audit
# For python: safety check (if installed)
```
