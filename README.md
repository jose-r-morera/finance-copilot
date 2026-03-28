# 💼 finance-copilot

> **Corporate Finance Autopilot** — A multi-agent AI pipeline for automated brand analysis, financial modeling, and strategic advisory.

[![CI](https://github.com/jose-r-morera/finance-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/jose-r-morera/finance-copilot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

`finance-copilot` is an agentic system designed to automate the heavy lifting of corporate finance analysis. It takes a public company ticker, ingests data from disparate sources (SEC filings, market data, brand materials), builds a triple-case financial model (Base, Upside, Downside), and generates a professional investment/credit case.

### Key Capabilities
- **Brand & Positioning Capture**: Automated scraping of investor materials and brand sources.
- **Financial Reasoning Layer**: Triple-scenario forecasting with sensitizable key drivers.
- **Agentic Pipeline**: Orchestrated via **LangGraph**, using specialized agents for retrieval, calculation, and reporting.
- **Structured Outputs**: Professional PDF/PPTX reports and financial models.

---

## 🏗️ Architecture

The system follows a modular, pipeline-oriented architecture:

1.  **Ingestion Layer**: Fetches data from yfinance, SEC EDGAR, and web scraping.
2.  **Validation Layer**: Uses **Pydantic** to ensure data integrity before modeling.
3.  **Modeling Engine**: A reasoning layer that builds forecasts based on historical trends and analyst-defined assumptions.
4.  **Reporting Engine**: Renders outputs into structured stakeholder-ready formats.
5.  **Multi-Agent Orchestrator**: Manages the flow between steps, allowing for loops, retries, and tool-calling.

---

---

## 🛠️ Tech Stack & Choices

| Component | Choice | Justification |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | High performance, native async support, excellent type safety. |
| **Orchestration** | **LangGraph** | Enables cyclic agent workflows and state management for complex multi-step reasoning. |
| **LLMs** | **GPT-4o / Gemini** | High reasoning capability for financial data interpretation. |
| **Data Handling** | **Pandas / Pydantic** | Industry standards for data manipulation and typed validation. |
| **Infrastructure** | **Docker Compose** | Ensures reproducibility across environments. |
| **Quality** | **Ruff / Mypy / Pytest** | Modern, fast tooling for linting, type-checking, and testing. |

---

## 🤖 Agentic Development (Antigravity)

This repository includes a `.agents` directory designed specifically for the **Antigravity** developer agent. It contains:
- **Skills**: Specialized instructions for managing the Python environment, Docker operations, and performing responsible web scraping.
- **Workflows**: Automated pipelines for project setup and quality verification.
- **Rules**: Strict development standards for formatting (Ruff), ethics (Responsible Scraping), and architecture (Open Source First).

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local dev)
- API Keys (OpenAI, SEC User-Agent, etc.)

### Quick Start (Docker)
1.  **Clone the repo**:
    ```bash
    git clone https://github.com/jose-r-morera/finance-copilot.git && cd finance-copilot
    ```
2.  **Config**:
    ```bash
    cp .env.example .env
    # Edit .env with your real API keys
    ```
3.  **Run**:
    ```bash
    docker compose up --build
    ```
4.  **Verify**: Visit [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🚦 Roadmap (Work Plan)

See [WORKPLAN.md](WORKPLAN.md) for a detailed phased breakdown of the hackathon development.

---

## 📜 Rules & Disclaimers

- **Educational Purpose Only**: This is a student hackathon project.
- **No Investment Advice**: All outputs must be treated as demonstrations, not financial recommendations.
- **Data Usage**: Compliant with SEC EDGAR and yfinance Terms of Service.

---

## 👥 Authors
- **José Ramón Morera** — [jose-r-morera](https://github.com/jose-r-morera)