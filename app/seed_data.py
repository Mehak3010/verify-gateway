"""
Seeded example 'AI agent outputs' for demoing the Verification Gateway
without needing live API keys. Each example includes the raw text plus
pre-baked search evidence so the pipeline runs end-to-end offline.
"""

EXAMPLES = {
    "clean_report": {
        "title": "✅ Clean Report (should pass)",
        "raw_output": (
            "Quarterly Compliance Summary: The company's revenue for FY2024 "
            "grew to $4.2B, up from $3.8B in FY2023. This aligns with the "
            "10-K filing submitted to the SEC. No material litigation was "
            "reported during this period."
        ),
        "mock_evidence": {
            "revenue for FY2024 grew to $4.2B": [
                "SEC 10-K filing confirms FY2024 revenue of approximately $4.2 billion, up from $3.8B in FY2023."
            ],
            "No material litigation was reported": [
                "Annual report legal proceedings section states no material pending litigation for the fiscal year."
            ],
        },
    },
    "fake_citation": {
        "title": "❌ Fabricated Legal Citation (should be rejected)",
        "raw_output": (
            "Legal Risk Memo: Per the ruling in Whitmore v. Alden Financial "
            "Corp, 2022 WL 481923 (9th Cir. 2022), companies are not required "
            "to disclose AI-driven credit scoring methodology to consumers. "
            "This precedent supports our proposed policy."
        ),
        "mock_evidence": {
            "Whitmore v. Alden Financial Corp, 2022 WL 481923 (9th Cir. 2022)": [
                "No case matching this citation was found in Westlaw, CourtListener, or Google Scholar search results.",
                "No record of a case titled 'Whitmore v. Alden Financial Corp' exists in 9th Circuit dockets for 2022.",
            ],
        },
    },
    "wrong_statistic": {
        "title": "⚠️ Plausible but Incorrect Statistic (should be flagged)",
        "raw_output": (
            "Market Analysis: According to Deloitte's State of AI report, "
            "over 70% of enterprises have piloted generative AI, and 45% "
            "have already scaled these pilots into full production "
            "deployments across their organization."
        ),
        "mock_evidence": {
            "45% have already scaled these pilots into full production": [
                "Deloitte's State of AI in the Enterprise report indicates only around 11-14% of organizations have scaled AI pilots into full production, far below the commonly cited figure.",
            ],
        },
    },
    "genw_agent_report": {
        "title": "❌ Low-Code Agent Compliance Report (fabricated regulation)",
        "raw_output": (
            "Vendor Risk Report (auto-generated): Under Section 14.7 of the "
            "Global Data Processing Directive (2023), third-party vendors "
            "handling AI-scored credit data must complete biannual audits. "
            "Our vendor completed 2 of 4 required audits this year, putting "
            "us at 50% compliance."
        ),
        "mock_evidence": {
            "Section 14.7 of the Global Data Processing Directive (2023)": [
                "No regulation titled 'Global Data Processing Directive' appears in EU, US, or UK regulatory registries.",
                "This citation does not match any known data protection statute; likely a fabricated regulatory reference.",
            ],
        },
    },
    "sap_agent_workflow": {
        "title": "⚠️ ERP Agent Handoff Note (unverifiable claim)",
        "raw_output": (
            "Workflow Update: The procurement agent auto-approved PO-88213 "
            "based on the vendor's historical on-time delivery rate of 98%, "
            "sourced from the SAP BTP vendor performance module."
        ),
        "mock_evidence": {},
    },
}
