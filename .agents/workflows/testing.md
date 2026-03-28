---
description: Pipeline to run automated tests for both backend and frontend.
---

# Workflow: Testing

This workflow ensures all components are verified before deployment.

### 1. Backend Tests (Pytest)
Run the backend test suite:
```bash
make test
```
Or directly via pytest:
```bash
pytest backend/tests/
```

### 2. Frontend Tests (Vitest/Jest)
Run frontend tests:
```bash
cd frontend && npm test
```

### 3. Integration Tests
Ensure both services are up:
```bash
make up
# Run integration scripts if available
```

### 4. Coverage (Optional)
Check code coverage:
```bash
pytest --cov=backend
```
