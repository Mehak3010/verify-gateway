"""
Search client for claim verification.

Modes:
- MOCK mode (default, no API key needed): returns pre-baked evidence from
  seed_data.py so the whole pipeline is demoable offline.
- LIVE mode: if TAVILY_API_KEY is set, performs real web searches per claim.
"""

import os
import requests
from app.builtin_facts import check_builtin_facts

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "").strip()
TAVILY_URL = "https://api.tavily.com/search"


def search_claim(claim_text: str, mock_evidence: dict | None = None) -> list[str]:
    """
    Returns a list of short evidence snippets relevant to the claim.
    Checks the built-in internal fact base first (always on, works for any
    input including custom pasted text), then falls back to seeded mock
    evidence or live web search depending on configuration.
    """
    builtin = check_builtin_facts(claim_text)
    if builtin:
        return builtin

    if TAVILY_API_KEY:
        return _live_search(claim_text)
    return _mock_search(claim_text, mock_evidence or {})


def _mock_search(claim_text: str, mock_evidence: dict) -> list[str]:
    for key, snippets in mock_evidence.items():
        if key.lower() in claim_text.lower() or claim_text.lower() in key.lower():
            return snippets
    # No matching seeded evidence -> simulate "nothing found"
    return []


def _live_search(claim_text: str) -> list[str]:
    try:
        resp = requests.post(
            TAVILY_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": claim_text,
                "search_depth": "basic",
                "max_results": 3,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [r.get("content", "")[:400] for r in data.get("results", [])]
    except Exception as e:
        return [f"[search_error] {e}"]
