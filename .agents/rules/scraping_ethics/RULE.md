---
name: scraping_ethics
description: Responsible and ethical data extraction patterns.
---

# Scraping Ethics Rule

This rule defines the ethical and technical boundaries for data extraction in this project.

## Standards
- **OSS First**: Prefer well-maintained open-source libraries (`yfinance`, `sec-edgar-downloader`) over custom scrapers.
- **Responsible**: Always include a descriptive `User-Agent` string.
- **Rate-Limiting**: Implement retries with exponential backoff (e.g., `tenacity`).
- **Compliance**: Respect `robots.txt` and Term of Service (TOS) of target sites.
- **Transparency**: Cite all data sources in the generated outputs.
