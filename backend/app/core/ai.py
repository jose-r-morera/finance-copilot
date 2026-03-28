"""Google Generative AI (Gemini) client for financial analysis."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_gemini_response(prompt: str, api_key: str = "") -> str:
    """Call Gemini API with a prompt. Returns empty string if not configured."""
    if not api_key:
        logger.warning("GOOGLE_API_KEY not set; returning stub AI response.")
        return _stub_response(prompt)

    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:  # noqa: BLE001
        logger.error("Gemini API error: %s", exc)
        return _stub_response(prompt)


def _stub_response(prompt: str) -> str:
    """Return a clearly-labelled stub when AI is not configured."""
    return (
        "[AI STUB – configure GOOGLE_API_KEY for real analysis] "
        f"Prompt received: {prompt[:120]}..."
    )
