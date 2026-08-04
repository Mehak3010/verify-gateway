from app.llm_client import extract_claims, judge_claim
from app.search_client import search_claim

# If any claim is contradicted, or unverifiable ratio exceeds this, reject.
UNVERIFIABLE_REJECT_THRESHOLD = 0.5


def verify_output(raw_text: str, mock_evidence: dict | None = None) -> dict:
    """
    Runs the full gateway pipeline on a piece of AI agent output.
    Returns a structured report: per-claim verdicts + overall decision.
    """
    claims = extract_claims(raw_text)

    results = []
    for claim in claims:
        evidence = search_claim(claim, mock_evidence)
        verdict = judge_claim(claim, evidence)
        results.append({
            "claim": claim,
            "evidence": evidence,
            "verdict": verdict["verdict"],
            "confidence": verdict["confidence"],
            "reason": verdict["reason"],
        })

    overall = _aggregate(results)

    return {
        "raw_output": raw_text,
        "claims_checked": len(results),
        "results": results,
        "overall_decision": overall["decision"],
        "overall_reason": overall["reason"],
    }


def _aggregate(results: list[dict]) -> dict:
    if not results:
        return {"decision": "PASS", "reason": "No checkable factual claims detected."}

    contradicted = [r for r in results if r["verdict"] == "contradicted"]
    unverifiable = [r for r in results if r["verdict"] == "unverifiable"]

    if contradicted:
        return {
            "decision": "REJECT",
            "reason": f"{len(contradicted)} claim(s) contradicted by evidence — likely hallucination.",
        }

    if len(unverifiable) / len(results) > UNVERIFIABLE_REJECT_THRESHOLD:
        return {
            "decision": "FLAG",
            "reason": f"{len(unverifiable)}/{len(results)} claims could not be verified — needs human review.",
        }

    return {"decision": "PASS", "reason": "All checkable claims verified against evidence."}
