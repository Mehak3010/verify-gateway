# Verification & Anti-Hallucination Gateway

A modular checkpoint that sits between a low-code / enterprise AI agent and
its end-user output. It extracts factual claims (statistics, citations,
legal references), checks each one against external evidence, and blocks
or flags anything unverified **before it reaches the UI**.

Built as a direct response to the friction point in Deloitte's [GenW.AI
low-code platform rollout](https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html):
enterprises are piloting AI agents faster than they can trust them, and
high-profile cases of AI tools citing fabricated legal references have made
"blind trust" the #1 blocker to moving pilots into production.

## What it does

```
Agent Output  →  Claim Extraction  →  Evidence Search  →  LLM/Heuristic Judge  →  Decision
   (text)          (LLM or regex)      (web search)       (verified/            (PASS /
                                                             contradicted/        FLAG /
                                                             unverifiable)        REJECT)
```

- **PASS** — every checkable claim was corroborated.
- **FLAG** — too many claims couldn't be verified either way → needs human review.
- **REJECT** — at least one claim was directly contradicted by evidence (e.g. a citation that doesn't exist).

## Demo mode vs. live mode

This runs **out of the box with zero API keys** using seeded example
reports and a rule-based extractor/judge — good for a first look.

Set these env vars to run it against real inputs:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Uses Claude for claim extraction + judging instead of regex heuristics |
| `TAVILY_API_KEY` | Uses live web search instead of seeded mock evidence |

## Quick start (local)

```bash
pip install -r requirements.txt

# API (FastAPI)
uvicorn app.main:app --reload
# -> http://localhost:8000/docs

# UI (Streamlit) — in a second terminal
streamlit run streamlit_app.py
# -> http://localhost:8501
```

## Quick start (Docker)

```bash
docker compose up --build
# API:  http://localhost:8000
# UI:   http://localhost:8501
```

To run with live search + Claude judging:

```bash
ANTHROPIC_API_KEY=sk-... TAVILY_API_KEY=tvly-... docker compose up --build
```

## API

```
GET  /examples                     list seeded demo reports
GET  /verify/example/{key}         run the gateway on a seeded report
POST /verify   {"text": "..."}     run the gateway on arbitrary text
```

## Seeded examples included

1. **Clean report** — passes verification cleanly.
2. **Fabricated legal citation** — mimics real incidents of AI tools citing
   non-existent case law; correctly rejected.
3. **Plausible-but-wrong statistic** — a subtly incorrect number dressed up
   as real Deloitte research; correctly flagged/rejected.

## Why this matters for production AI rollouts

Deloitte's own research shows the gap isn't model capability — it's trust
infrastructure. Only ~11-14% of enterprise AI pilots reach production,
and a recurring cause is that outputs go straight from model to user with
no verification layer in between. This gateway is a small, pluggable
proof of concept for that missing layer: it doesn't try to make the model
smarter, it makes the *pipeline* accountable for what the model says before
a human ever sees it.

## Architecture notes / next steps

- Claim extraction and judging are pluggable (`app/llm_client.py`) — swap
  in any LLM provider.
- Evidence retrieval is pluggable (`app/search_client.py`) — swap Tavily
  for an internal document/RAG index for domain-specific verification.
- Natural extension: adversarial red-teaming (auto-generating edge-case
  prompts to stress-test an agent's outputs before deployment) — out of
  scope for this prototype but a straightforward next module.
