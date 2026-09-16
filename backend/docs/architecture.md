# System Architecture: AppleSupport AI Agent

## 1. High-Level System Architecture

```text
                    ┌──────────────────────┐
                    │ Customer Message     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Intent Classifier    │
                    │ (Dense all-MiniLM    │
                    │ + Calibrated LR)     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Escalation Policy    │
                    │ Guardrails Engine    │
                    └───────┬───────┬──────┘
                            │       │
                     AUTO HANDLE   ESCALATE ────► [Human Tier-2 Handoff]
                            │       │            (Genius Bar / Specialist)
                            ▼       ▼
                 ┌─────────────────────────┐
                 │ Historical Retrieval    │
                 │ (8k Dense Pairs,        │
                 │  Zero Leakage Parquet)  │
                 └──────────┬──────────────┘
                            │
                            ▼
                 ┌─────────────────────────┐
                 │ Supporting Evidence     │
                 │ (Top-3 Cosine Ranked    │
                 │  Historical Solutions)  │
                 └──────────┬──────────────┘
                            │
                            ▼
                 ┌─────────────────────────┐
                 │ Response Generator      │
                 │ (Grounded Synthesis +   │
                 │  Verified Apple KB URLs)│
                 └──────────┬──────────────┘
                            │
                            ▼
                 ┌─────────────────────────┐
                 │ Draft Reply +           │
                 │ Machine Reason Code     │
                 └─────────────────────────┘
```

---

## 2. Component Descriptions

### A. Data Ingestion & Sanitization (`src/data/`)
- Streams conversation pairs from the Kaggle Twitter Customer Support dataset.
- Filters PII (credit cards, phone numbers, email addresses, user handles).
- Enforces strict zero-leakage separation: all 200 Golden Evaluation cases are excised from the retrieval index.

### B. Intent Classifier (`src/intents/`)
- Encodes incoming text using `all-MiniLM-L6-v2` into 384-dimensional dense vectors.
- Applies `CalibratedClassifierCV(LogisticRegression)` across 8 empirical classes.
- Generates predicted intent, calibrated confidence, and alternative class rankings.

### C. Escalation Policy & Guardrail Engine (`src/escalation/`)
- Evaluates safety hazard regexes (`swollen`, `fire`, `smoke`, `spark`).
- Intercepts physical hardware damage (`shattered`, `cracked screen`) and routes to Genius Bar.
- Intercepts compromised credentials / unauthorized transactions.
- Enforces threshold guards: intent confidence $\ge 0.58$, retrieval similarity $\ge 0.50$.
- Uses asymmetric cost matrix: $C_{\text{False Auto-Handle}} = 5.0$ vs. $C_{\text{False Escalate}} = 1.0$.

### D. Historical Resolution Retrieval Engine (`src/retrieval/`)
- Cosine dot-product similarity search over 8,000 unit-normalized historical resolution vectors.
- Retrieval latency: $< 1.5\text{ ms}$ per query on standard CPU.
- Returns top-3 ranked supporting evidence pairs with similarity scores.

### E. Grounded Response Generator (`src/generation/`)
- Synthesizes empathetic customer support replies grounded in retrieved historical steps.
- Injects verified official Apple Knowledge Base anchors (`support.apple.com`, `iforgot.apple.com`, `reportaproblem.apple.com`).
- Constrained against hallucinating non-existent refunds, false warranties, or synthetic account lookups.

### F. API & Interactive Demonstration Dashboard (`backend/main.py`)
- FastAPI service serving `POST /predict`, `POST /evaluate`, `GET /health`, and `GET /config`.
- Real-time interactive web UI with live query analysis, evidence inspection, and golden evaluation browsing.
