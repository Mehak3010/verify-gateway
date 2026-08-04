"""
A tiny always-on 'internal knowledge base' — represents the kind of curated,
pre-verified facts a real enterprise gateway would keep in an internal RAG
index (compliance policies, known-good stats, prior fact-check rulings).

Unlike the per-seeded-example mock_evidence in seed_data.py, these entries
apply to ANY input text (including custom pasted text), so the demo has
something to check against even with zero API keys configured.
"""

import re

# (regex pattern to match in claim text, evidence snippets to return)
BUILTIN_FACTS = [
    (
        re.compile(r"\bpilots?\b.{0,60}\bproduction\b", re.IGNORECASE),
        [
            "Deloitte's State of AI in the Enterprise report indicates only "
            "around 11-14% of organizations have scaled AI pilots into full "
            "production, far below commonly cited higher figures."
        ],
    ),
    (
        re.compile(r"\b\d{4}\s?WL\s?\d+\b", re.IGNORECASE),  # Westlaw citation format
        [
            "No record of this citation exists in the verified case-law index. "
            "Citation format alone does not confirm the case is real; this "
            "requires human legal review before use."
        ],
    ),
]


def check_builtin_facts(claim_text: str) -> list[str]:
    """Returns evidence snippets from the built-in fact base that match
    this claim, or an empty list if nothing applies."""
    for pattern, snippets in BUILTIN_FACTS:
        if pattern.search(claim_text):
            return snippets
    return []
