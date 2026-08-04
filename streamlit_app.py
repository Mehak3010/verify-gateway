import streamlit as st
from app.verifier import verify_output
from app.seed_data import EXAMPLES

st.set_page_config(page_title="Verification & Red-Teaming Gateway", layout="wide")

st.title("🛡️ Verification & Anti-Hallucination Gateway")
st.caption(
    "A modular checkpoint for low-code AI agent output — catches fabricated "
    "citations and unverifiable claims before they reach the end user."
)

VERDICT_STYLE = {
    "verified": ("✅", "green"),
    "contradicted": ("❌", "red"),
    "unverifiable": ("⚠️", "orange"),
}

DECISION_STYLE = {
    "PASS": ("🟢 PASS", "green"),
    "FLAG": ("🟡 FLAG FOR REVIEW", "orange"),
    "REJECT": ("🔴 REJECT", "red"),
}

with st.sidebar:
    st.header("Input")
    mode = st.radio("Choose input mode", ["Seeded example", "Paste custom text"])

    example_key = None
    custom_text = ""

    if mode == "Seeded example":
        example_key = st.selectbox(
            "Example agent output",
            options=list(EXAMPLES.keys()),
            format_func=lambda k: EXAMPLES[k]["title"],
        )
    else:
        custom_text = st.text_area(
            "Paste AI-generated report / agent output",
            height=200,
            placeholder="Paste text containing claims, stats, or citations to verify...",
        )

    run = st.button("Run through Gateway ▶", type="primary", use_container_width=True)

if run:
    if mode == "Seeded example":
        example = EXAMPLES[example_key]
        report = verify_output(example["raw_output"], example.get("mock_evidence"))
    else:
        if not custom_text.strip():
            st.warning("Paste some text first.")
            st.stop()
        report = verify_output(custom_text)

    st.subheader("Raw Agent Output")
    st.code(report["raw_output"], language=None)

    decision_label, decision_color = DECISION_STYLE.get(report["overall_decision"], ("UNKNOWN", "gray"))
    st.markdown(f"### Gateway Decision: :{decision_color}[{decision_label}]")
    st.write(report["overall_reason"])

    st.subheader(f"Claim-Level Breakdown ({report['claims_checked']} claim(s) checked)")

    if not report["results"]:
        st.info("No independently checkable factual claims were detected in this text.")
    else:
        for r in report["results"]:
            icon, color = VERDICT_STYLE.get(r["verdict"], ("❓", "gray"))
            with st.expander(f"{icon} {r['claim']}", expanded=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**Verdict:** :{color}[{r['verdict'].upper()}]")
                    st.markdown(f"**Confidence:** {r['confidence']:.2f}")
                with col2:
                    st.markdown(f"**Reason:** {r['reason']}")
                    if r["evidence"]:
                        st.markdown("**Evidence found:**")
                        for e in r["evidence"]:
                            st.markdown(f"- {e}")
                    else:
                        st.markdown("**Evidence found:** _none_")
else:
    st.info("Choose an example or paste text in the sidebar, then click **Run through Gateway**.")
