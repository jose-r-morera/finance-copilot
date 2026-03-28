# Deployment Plan: Finance Copilot (Hobby vs. Production)

This document provides two distinct paths for deploying the Finance Copilot stack. Both use **Langfuse** for observability.

---

## 🛠️ Phase 0: Universal Setup (Langfuse)
Regardless of the scenario, start by setting up your observability layer:
1. Create a free account at [Langfuse](https://cloud.langfuse.com).
2. Create a new project: `Finance-Copilot`.
3. In **Settings**, generate your `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`.
4. Copy these to your environment configuration (see Phases below).

---

## 🏎️ Scenario A: Hobby / MVP Deployment
**Goal**: Zero cost, fast setup, perfect for demos.

### 1. Data Layer (Upstash Redis)
- Create a Free Tier Redis instance on [Upstash](https://upstash.com).
- Copy the `REDIS_URL`.

### 2. Backend (Render.com)
- Deploy as a **Web Service** using the Dockerfile.
- **Select**: Free Instance ($0/mo).
- **Environment Variables**:
    - `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`
    - `REDIS_URL`, `OPENAI_API_KEY`, `SEC_EDGAR_USER_AGENT`
- *Note*: First request after 15m of inactivity will be slow (spin-down).

### 3. Frontend (Vercel)
- Link the `frontend/` directory to **Vercel**.
- Add `NEXT_PUBLIC_API_URL` pointing to your Render URL.

---

## 🏛️ Scenario B: Enterprise Production Grade
**Goal**: Sustained performance, no cold starts, 99.9% availability.

### 1. Data Layer (Upstash / AWS Elasticache)
- Use **Upstash Professional** or **AWS Elasticache** for dedicated Redis resources.
- Enable automatic backups and multi-AZ replication.

### 2. Backend (Render Pro / AWS App Runner / Fly.io)
- **Select**: Paid Instance (Starter or Pro).
- **Configuration**:
    - **Minimum Instances**: 2 (for high availability).
    - **Autoscaling**: Trigger based on CPU/RAM usage.
- **Environment**: Use secret management services (like AWS Secrets Manager or Render Secrets).

### 3. Frontend (Vercel Pro)
- Use **Vercel Pro** for faster builds, DDoS protection, and detailed web analytics.

### 4. Advanced Observability (Langfuse Pro)
- Use Langfuse's **Prompt Management** to version control LLM prompts without code deploys.
- Set up **Evaluations** to automatically score agent outputs.

---

## ✅ Final Verification (CORS Audit)
Update `backend/app/main.py` before pushing to Scenario B:
```python
# PRODUCTION: Specify your Vercel URL explicitly
allow_origins = [
    "https://your-app-name.vercel.app",
    "https://your-custom-domain.com"
]
```
