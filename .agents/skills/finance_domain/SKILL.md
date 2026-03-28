---
name: finance_domain
description: Specialized knowledge for corporate finance data models and logic.
---

# Finance Domain Skill

This skill encompasses the domain logic for the Finance Copilot.

## Core Concepts
- **Financial Statements**: Balance Sheets, Income Statements, Cash Flow Statements.
- **KPIs**: EBITDA, ROI, Working Capital, Current Ratio.
- **Forecasting**: Time-series analysis, budget variance analysis.

## Data Structures
- **Transaction**: `id`, `date`, `amount`, `category`, `description`.
- **Account**: `id`, `name`, `type` (Asset, Liability, Equity).

## Best Practices
- **Precision**: Use `Decimal` types for all monetary calculations (avoid floats).
- **Validation**: Strict validation for date ranges and account balances.
- **Traceability**: Every financial figure must be traceable back to its source data.
