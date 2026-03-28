---
name: project_infra
description: Infrastructure and security standards (Docker, Secrets, OSS).
---

# Project Infrastructure Rule

This rule defines the infrastructure and security standards for the project.

## Standards
- **Docker First**: All services must be buildable via `docker compose`.
- **Secrets Management**: NEVER hardcode API keys or secrets. Use environment variables via `.env`.
- **Open Source First**: Prioritize naming and justifying all third-party libraries and tools used. Prefer composing existing building blocks over reinventing.
- **Production Mindset**: Ensure configuration, error handling, and testable code at every step.
