---
description: Pipeline to verify code quality and health of the project.
---

# Workflow: Quality Check

1. **Lint & Format**: Run `make format` then `make lint`.
2. **Type Check**: Run `make typecheck`.
3. **Test**: Run `make test`.
4. **Docker Health**: (Optional) Run `make up` and check the health endpoint.
