from fastapi import FastAPI
from pydantic import BaseModel
from app.verifier import verify_output
from app.seed_data import EXAMPLES

app = FastAPI(
    title="Verification & Anti-Hallucination Gateway",
    description="Intercepts low-code / agent-generated output and flags unverified claims before they reach the UI.",
    version="0.1.0",
)


class VerifyRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ok", "service": "verification-gateway"}


@app.get("/examples")
def list_examples():
    return {key: val["title"] for key, val in EXAMPLES.items()}


@app.post("/verify")
def verify(req: VerifyRequest):
    return verify_output(req.text)


@app.get("/verify/example/{example_key}")
def verify_example(example_key: str):
    example = EXAMPLES.get(example_key)
    if not example:
        return {"error": f"Unknown example '{example_key}'. Try one of: {list(EXAMPLES.keys())}"}
    return verify_output(example["raw_output"], example.get("mock_evidence"))
