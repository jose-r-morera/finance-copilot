---
name: finance_logic
description: Rules for ensuring accuracy and reliability in financial data.
---

# Finance Logic Rule

## Accuracy Requirements
1. **No Rounding Errors**: All currency rounding must follow standard accounting principles (usually half-to-even).
2. **Immutability**: Historical financial records must never be modified directly; use adjustment entries.
3. **Auditability**: Every change to a financial state must be logged with a timestamp and user ID.

## Implementation Rules
- **Decimals**: Always use `decimal.Decimal` in Python for financial math.
- **Dates**: Use ISO 8601 formatted strings or `datetime` objects with timezone info.
- **Categories**: Use a fixed set of categories for classification to ensure consistency.
