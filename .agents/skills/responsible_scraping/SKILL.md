---
name: responsible_scraping
description: Ethical data extraction patterns, adhering to rate limits and User-Agent requirements.
---

# Responsible Scraping Skill

This skill provides instructions for the Antigravity developer agent to perform data extraction while respecting third-party terms and technical constraints.

## Tools Summary
- `yfinance`: Use as a primary source for market data (avoids direct scraping).
- `sec-edgar-downloader`: Respects SEC polling limits.
- `beautifulsoup4`: For site-specific IR page scraping (if necessary).

## Usage Guidelines
- **Always** set a descriptive `User-Agent`.
- **Never** perform parallel scraping without rate-limiting.
- Prefer official APIs (yfinance, EDGAR) over raw scraping.
- Respect `robots.txt` where applicable.
