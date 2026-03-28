# =============================================================================
# finance-copilot — frontend/Dockerfile
# Multi-stage build: builder → development | production
# =============================================================================

# --------------- Stage 1: builder -------------------------------------------
FROM node:20-slim AS builder

WORKDIR /build

# Copy manifest files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# --------------- Stage 2: development ---------------------------------------
FROM node:20-slim AS development

WORKDIR /app

# Copy node_modules from builder
COPY --from=builder /build/node_modules ./node_modules

# Source will be mounted as a volume in docker-compose for hot-reload
# Using root for development stage to avoid UID/GID permission issues with host mounts
EXPOSE 3000

CMD ["npm", "run", "dev"]

# --------------- Stage 3: production ----------------------------------------
FROM node:20-slim AS production

WORKDIR /app

ENV NODE_ENV=production

# Copy node_modules
COPY --from=builder /build/node_modules ./node_modules

# Bake in source
COPY . .

# Build Next.js
RUN npm run build

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 3000

CMD ["npm", "run", "start"]
