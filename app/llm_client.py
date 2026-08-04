"""
LLM client for two jobs:
  1. Extract factual/checkable claims from an agent's output.
  2. Judge each claim against retrieved evidence -> verdict + confidence.

If ANTHROPIC_API_KEY is set, both jobs use Claude (claude-sonnet-4-6).
Otherwise, a lightweight heuristic fallback runs so the whole pipeline
still works with zero setup (good for a first demo / offline run).
"""

import os
import re
import json
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"


def _call_claude(system: str, user: str) -> str:
    resp = requests.post(
        ANTHROPIC_URL,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 1000,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------

def extract_claims(text: str) -> list[str]:
    if ANTHROPIC_API_KEY:
        return _extract_claims_llm(text)
    return _extract_claims_heuristic(text)


def _extract_claims_llm(text: str) -> list[str]:
    system = (
        "You extract discrete, independently fact-checkable claims (statistics, "
        "citations, legal references, named facts) from text. "
        "Respond ONLY with a JSON array of strings, no preamble, no markdown fences."
    )
    raw = _call_claude(system, text)
    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        claims = json.loads(cleaned)
        if isinstance(claims, list):
            return [str(c) for c in claims]
    except Exception:
        pass
    return _extract_claims_heuristic(text)


_ABBREVIATIONS = ["v.", "Cir.", "Inc.", "Corp.", "WL", "No.", "Ltd.", "U.S.", "vs."]
_PLACEHOLDER = "\u0000"  # unlikely to appear in real text


def _extract_claims_heuristic(text: str) -> list[str]:
    """Simple rule-based fallback: sentences containing numbers, %, $,
    case-citation patterns, or years are treated as checkable claims.
    Protects common legal/corporate abbreviations (v., Cir., Corp., etc.)
    from being mistaken for sentence boundaries."""
    protected = text
    for abbr in _ABBREVIATIONS:
        protected = protected.replace(abbr, abbr.replace(".", _PLACEHOLDER))

    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", protected.strip())
    sentences = [s.replace(_PLACEHOLDER, ".") for s in sentences]

    signal_pattern = re.compile(
        r"(\d|%|\$|v\.\s|WL\s\d|Cir\.|according to|per the ruling)", re.IGNORECASE
    )
    return [s.strip() for s in sentences if s.strip() and signal_pattern.search(s)]


# ---------------------------------------------------------------------------
# Claim judging
# ---------------------------------------------------------------------------

def judge_claim(claim: str, evidence: list[str]) -> dict:
    if ANTHROPIC_API_KEY:
        return _judge_claim_llm(claim, evidence)
    return _judge_claim_heuristic(claim, evidence)


def _judge_claim_llm(claim: str, evidence: list[str]) -> dict:
    system = (
        "You are a fact-verification judge. Given a CLAIM and EVIDENCE snippets, "
        "decide a verdict: 'verified', 'contradicted', or 'unverifiable'. "
        "Respond ONLY with JSON: "
        '{"verdict": "...", "confidence": 0-1, "reason": "..."} no markdown fences.'
    )
    user = f"CLAIM: {claim}\n\nEVIDENCE:\n" + "\n".join(f"- {e}" for e in evidence) if evidence else \
           f"CLAIM: {claim}\n\nEVIDENCE: (none found)"
    raw = _call_claude(system, user)
    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(cleaned)
        return {
            "verdict": result.get("verdict", "unverifiable"),
            "confidence": float(result.get("confidence", 0.5)),
            "reason": result.get("reason", ""),
        }
    except Exception:
        return _judge_claim_heuristic(claim, evidence)


def _judge_claim_heuristic(claim: str, evidence: list[str]) -> dict:
    if not evidence:
        return {"verdict": "unverifiable", "confidence": 0.4,
                "reason": "No corroborating evidence found via search."}

    joined = " ".join(evidence).lower()
    contradiction_signals = [
        "no case matching", "no record", "far below", "not found", "incorrect", "false",
        "does not match", "does not exist", "fabricated", "no regulation", "not appear",
        "no such", "cannot be verified as accurate", "contradicts",
    ]
    if any(sig in joined for sig in contradiction_signals):
        return {"verdict": "contradicted", "confidence": 0.85,
                "reason": "Evidence explicitly contradicts or fails to corroborate the claim."}

    return {"verdict": "verified", "confidence": 0.75,
            "reason": "Evidence snippets corroborate the claim."}
