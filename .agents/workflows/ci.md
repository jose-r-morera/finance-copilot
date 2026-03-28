---
description: Pipeline for Continuous Integration checks.
---

# Workflow: CI Pipeline

Standard checks to be run on every pull request or push to main.

### 1. Unified Quality Check
Runs linting, typechecking, and all backend tests in a clean environment:
```bash
make docker-check
```
For frontend specific:
```bash
cd frontend && npm run lint
```

### 2. Automated Testing
Execute the full backend and frontend test suites:
```bash
make docker-test
cd frontend && npm test
```

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
