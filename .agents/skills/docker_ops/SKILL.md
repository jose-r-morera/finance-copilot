---
name: docker_ops
description: Orchestrating the backend and redis services via Docker Compose.
---

# Docker Operations Skill

This skill provides instructions for the Antigravity developer agent to manage the project's infrastructure using Docker.

## Tools Summary
- `docker compose`: Orchestrate multi-container services.
- `Dockerfile`: Multi-stage builds for backend.

## Usage Guidelines
- Use `make up` to start the development environment.
- Use `make down` to stop all services.
- Always verify the health endpoint after a build: `curl http://localhost:8000/api/v1/health`.
