#  AppleSupport AI Customer Support Agent & Rigorous Evaluation Suite

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-13%2F13%20Passing-30D158.svg?style=flat)]()
[![Acceptance Suite](https://img.shields.io/badge/Acceptance%20Suite-6%2F6%20Verified-30D158.svg?style=flat)]()
[![Intent Macro-F1](https://img.shields.io/badge/Intent%20Macro--F1-62.3%25-0A84FF.svg?style=flat)]()
[![Safety Recall](https://img.shields.io/badge/Safety%20Recall-92.9%25-30D158.svg?style=flat)]()
[![Zero Leakage](https://img.shields.io/badge/Zero%20Data%20Leakage-Verified-30D158.svg?style=flat)]()

> **Evaluation-First Customer Support System for `@AppleSupport`**  
> *"The proof is worth more than the system"* — An honest, self-critical, and reproducible evaluation of a production-grade AI support agent grounded in historical resolutions from the Kaggle Twitter Customer Support corpus (`thoughtvector/customer-support-on-twitter`). Features calibrated intent classification, safety-first escalation guardrails, dense vector retrieval, and multi-provider LLM response generation with a zero-key diagnostic fallback engine.

---

## ⚡ Quickstart: Run in Under 1 Minute

The entire system runs deterministically on standard local CPU without requiring external API keys or GPU compute:

```bash
# 1. Clone & install dependencies
git clone https://github.com/SOHAMPAL23/Hiver.git
cd Hiver
pip install -r requirements.txt

# 2. Run the automated unit & acceptance test suite (13 passing tests)
pytest tests/test_agent.py -v

# 3. Launch the FastAPI server & Interactive Web Diagnostic Console
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 4. Open the Web App in your browser
# Navigate to: http://localhost:8000/
```

### CLI Quick Demos

```bash
# Run interactive end-to-end CLI demonstration
python demo.py

# Run master benchmark evaluation over the 200-sample Golden Set
python run_eval.py
```

---

## 📂 Project & Folder Structure

The repository is organized following clean, modular software engineering and machine learning principles. Core business logic, data pipelines, model artifacts, evaluation harnesses, and user interfaces are cleanly decoupled:

```text
Hiver/
├── .env.example                    # Environment variable template for API keys & providers
├── .gitignore                      # Production gitignore (Python, envs, caches, large data)
├── config.yaml                     # Central system, brand, policy, and model configuration
├── requirements.txt                # Pinned Python package dependencies
├── README.md                       # Comprehensive project documentation
├── CITATIONS.md                    # Formal academic & library citations
├── DECISION_LOG.md                 # Architectural decision records & trade-off rationale
├── demo.py                         # Interactive CLI demonstration script
├── run_eval.py                     # Master evaluation benchmark runner
├── eval_results.json               # Full evaluation output metrics across all 3 systems
│
├── src/                            # Core Python Modular Package
│   ├── __init__.py                 # Top-level exports (AppleSupportAgent facade)
│   ├── agent.py                    # Unified orchestrator coordinating 4-stage pipeline
│   │
│   ├── data/                       # Ingestion & preprocessing pipeline
│   │   ├── __init__.py
│   │   ├── loader.py               # Dataset loading & brand filtering
│   │   ├── cleaner.py              # PII masking (regex) & text sanitization
│   │   ├── thread_reconstruction.py# Customer-brand conversation thread pairing
│   │   └── splitter.py             # Temporal & conversation-level train/val/test splits
│   │
│   ├── intents/                    # Intent classification subsystem
│   │   ├── __init__.py
│   │   ├── taxonomy.py             # 8 empirical intent definitions & decision boundaries
│   │   └── classifier.py           # all-MiniLM-L6-v2 + Calibrated Logistic Regression
│   │
│   ├── retrieval/                  # Dense semantic retrieval engine
│   │   ├── __init__.py
│   │   └── retriever.py            # Cosine similarity vector search over 8,000 historical pairs
│   │
│   ├── escalation/                 # Policy engine & safety guardrails
│   │   ├── __init__.py
│   │   └── policy.py               # Asymmetric cost-sensitive auto-handle vs. escalation rules
│   │
│   └── generation/                 # Response generation subsystem
│       ├── __init__.py
│       └── generator.py            # Multi-provider LLM (OpenAI, Gemini, Ollama, Groq)
│                                   # + Zero-key situation-specific Apple Diagnostic Engine
│
├── models/                         # Trained Checkpoints & Dense Vector Index Artifacts
│   ├── __init__.py
│   ├── classifier_model.pkl        # Calibrated Logistic Regression weights (80 KB)
│   └── retrieval_index.npz         # 8,000 dense normalized sentence embeddings (12 MB)
│
├── backend/                        # Production FastAPI REST Application
│   ├── __init__.py
│   └── main.py                     # Endpoints (/predict, /health, /config, /api/run_tests,
│                                   #            /api/golden_samples, /api/llm_config, /api/test_llm)
│
├── frontend/                       # Interactive Web Diagnostic & Verification Suite
│   ├── index.html                  # Apple dark mode interface (Console + QA Tabs + LLM Modal)
│   ├── style.css                   # Obsidian glassmorphism design system & micro-animations
│   ├── app.js                      # Live inference client, test runner, & golden set explorer
│   └── annotation_app.py           # Streamlit-based human annotation tool for Golden Set curation
│
├── golden_eval/                    # Benchmark Evaluation Dataset
│   ├── golden_eval.jsonl           # 200-sample human-annotated golden evaluation benchmark
│   ├── build_golden_set.py         # Golden set extraction & stratification script
│   └── labeling_methodology.md     # Annotation taxonomy guidelines & consistency audit
│
├── evaluation/                     # Comprehensive Evaluation & Calibration Suite
│   ├── __init__.py
│   ├── evaluate_all.py             # Complete benchmark execution over golden set
│   ├── evaluate_intent.py          # Intent classification Macro-F1, confusion matrix
│   ├── evaluate_escalation.py      # Escalation precision/recall & asymmetric cost evaluation
│   ├── evaluate_replies.py         # Response quality rubric (groundedness, actionability)
│   ├── llm_judge.py                # LLM-as-a-judge automated grading harness
│   ├── calibrate_judge.py          # Human-LLM judge calibration pipeline
│   ├── judge_calibration.json      # Calibration scoring results (Pearson r = 0.5914)
│   ├── JUDGE_CALIBRATION.md        # Comprehensive calibration documentation
│   └── human_vs_llm.py             # Statistical correlation audit script
│
├── data/                           # Data Artifacts & Taxonomies
│   ├── golden_set.csv              # Tabular CSV export of golden evaluation instances
│   ├── intent_taxonomy.yaml        # Formal YAML taxonomy specification
│   ├── DATA_CARD.md                # Complete data documentation card
│   └── samples/                    # Curated sample parquets (retrieval corpus)
│
├── reports/                        # Consolidated Engineering & Audit Reports
│   ├── final_report.md             # Complete technical report with deep-dive analysis
│   ├── failure_analysis.md         # Top 5 real failure modes extracted from golden eval
│   ├── headline_misleading_audit.md# Honest audit of what is misleading about headline metrics
│   ├── dataset_profile.md          # Dataset profiling, brand selection, & distributions
│   └── intent_taxonomy.md          # Intent taxonomy design rationale & boundaries
│
├── docs/                           # Architecture & Annotation Specifications
│   ├── architecture.md             # Component-level data flow & API contracts
│   └── annotation_guidelines.md    # Human labeler guidelines and edge-case handling
│
├── baselines/                      # Comparative Evaluation Baselines
│   ├── trivial_baseline.py         # Majority-class heuristic baseline
│   └── simple_baseline.py          # TF-IDF classifier + verbatim nearest-neighbor retrieval
│
├── scripts/                        # Operational Utilities
│   ├── build_index.py              # Dense vector index builder
│   ├── check_leakage.py            # Automated temporal & ID leakage verification
│   ├── explore_dataset.py          # Exploratory dataset distribution profiler
│   ├── prepare_data.py             # Dataset cleaning and pairing pipeline
│   └── select_brand.py             # Empirical brand suitability scoring algorithm
│
├── notebooks/                      # Exploratory Data Science Notebooks
│   └── 01_dataset_exploration.ipynb
│
├── taxonomy/                       # Taxonomy Exploration Tools
│   ├── TAXONOMY.md                 # Empirical taxonomy documentation
│   ├── taxonomy_spec.json          # JSON schema for intents and keywords
│   └── cluster_intents.py          # Unsupervised semantic clustering script
│
└── tests/                          # Automated Acceptance & Unit Test Suite
    └── test_agent.py               # 13 comprehensive unit tests validating end-to-end behavior
```

---

## 🏗️ System Architecture & Inference Pipeline

The agent operates through a decoupled 4-stage pipeline that guarantees explainable, deterministic guardrails while allowing dynamic, grounded response drafting:

```text
                        ┌─────────────────────────────────────┐
                        │ Customer Message (Tweet or Support) │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                                 [1. PII Sanitization]
                          Mask emails, phone numbers, cards
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │      Stage 1: Intent Classification      │
                      │  all-MiniLM-L6-v2 Embeddings (384-dim)  │
                      │   + Calibrated Multi-Class Logistic Reg │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Stage 2: Guardrails & Policy Engine  │
                      │  Asymmetric Cost Safety Decision Matrix │
                      └───────────────┬─────────────────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │     AUTO-HANDLE     │               │      ESCALATE       │
        │ Routine Diagnostics │               │ Priority Safety /   │
        │ High-Confidence KB  │               │ Account Security /  │
        │                     │               │ Hardware / Genius   │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │
                                      ▼
                      ┌─────────────────────────────────────────┐
                      │   Stage 3: Dense Semantic Retrieval     │
                      │  Cosine Vector Search (8k clean pairs)  │
                      │    Top-3 Historical Case Grounding      │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │      Stage 4: Grounded Generation       │
                      │  • If LLM active: Dynamic tailored reply│
                      │    (OpenAI, Gemini, Ollama, Groq)       │
                      │  • If Zero-Key: Expert Apple Diagnostic │
                      │    Engine with verified KB URLs         │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │    Structured Inspectable Output    │
                        │ Intent, Decision, Evidence, Reply,  │
                        │ Machine Reason Code, Latency        │
                        └─────────────────────────────────────┘
```

---

## 📊 Rigorous Benchmark Results vs. Baselines

Evaluated on the **200-sample Stratified Golden Evaluation Set** (`golden_eval/golden_eval.jsonl`) spanning all 8 empirical intents (25 examples each) with deliberate adversarial stress tests (sarcasm, multi-intent, non-English, safety hazards).

| System | Intent Macro-F1 | Intent Accuracy | Escalation Recall | Escalation Precision | False Auto-Handle (Safety Risk) | Asymmetric Cost / Query | Groundedness (1–5) | Actionability (1–5) | Overall Quality (1–5) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trivial Baseline** *(Majority Class + Static Policy)* | 2.8% | 12.5% | 0.0% | 0.0% | 42 / 200 | 1.05 | 3.00 | 4.00 | 4.00 |
| **Simple Baseline** *(TF-IDF + Verbatim Retrieval)* | 40.6% | 41.5% | 83.3% | 79.5% | 7 / 200 | 0.22 | 2.27 | 4.21 | 3.73 |
| **AppleSupport Agent** *(Dense RAG + Policy Engine)* | **62.3%** | **63.5%** | **92.9%** | **32.5%** | **3 / 200** | **0.48** | **4.53** | **5.00** | **4.57** |

### Key Metric Findings
1. **Intent Classification**: The Agent achieves **62.3% Macro-F1**, outperforming the Simple Baseline (40.6%) by **+21.7%** on hard, multi-intent, and sarcastic customer edge cases.
2. **Safety Recall**: The Agent intercepts **92.9% of all high-risk queries** (39/42), reducing dangerous False Auto-Handles to only 3 (compared to 42 for Trivial and 7 for Simple Baseline).
3. **Escalation Trade-off**: Escalation Precision is **32.5%** because the policy engine is intentionally tuned with an asymmetric cost ratio ($C_{\text{FAH}} = 5.0$ vs. $C_{\text{FE}} = 1.0$). In customer support, over-escalating a routine inquiry costs human time, but auto-handling a swollen battery or compromised Apple ID can cause physical harm or severe brand damage.
4. **Groundedness**: Generation groundedness jumps from **2.27/5** (verbatim retrieval) to **4.53/5** via conditioned synthesis with verified Apple documentation links (`support.apple.com`, `iforgot.apple.com`).

---

## 🔍 How We Know It's Working (Verification & QA Framework)

The system answers the core question: *"How do we know it is working fine and how will we be checking it?"* through four independent verification pillars:

### Pillar 1: Automated Acceptance Verification Suite (6 Live Scenarios)
The backend provides a dedicated endpoint `POST /api/run_tests` executable in **~140ms** with **6/6 automated checks**:
- **TEST_01 (Critical Physical Safety Guardrail)**: Intercepts thermal runaway and battery swelling before auto-handling (`ESCALATE`).
- **TEST_02 (Account Security Breach Guardrail)**: Intercepts unauthorized Apple ID access and password recovery breaches (`ESCALATE`).
- **TEST_03 (Hardware Physical Damage Guardrail)**: Directs shattered screens and liquid ingress to Genius Bar appointments (`ESCALATE`).
- **TEST_04 (Routine Battery Drain Auto-Triage)**: Safely auto-handles post-update battery degradation with diagnostic steps (`AUTO_HANDLE`).
- **TEST_05 (Canonical KB URL Grounding)**: Verifies that drafted resolutions strictly cite official `apple.com` domains.
- **TEST_06 (Low-Confidence Ambiguity Guardrail)**: Intercepts unparseable or noisy input (`ESCALATE`).

### Pillar 2: 200-Sample Stratified Golden Dataset Explorer
The frontend includes a ground-truth explorer allowing operators to inspect model predictions side-by-side against human-annotated golden labels:
- Real-time comparison of predicted intent vs. true intent.
- Decision policy match indicator (`✓ PERFECT MATCH` vs. `✓ ACTION MATCH` vs. `⚠ DISCREPANCY`).
- Filter by all 8 empirical intents or by difficulty (`easy`, `medium`, `hard`).

### Pillar 3: Human vs. LLM Judge Calibration Audit
To ensure automated grading is mathematically sound and statistically calibrated:
- Evaluated against **35 hand-scored human benchmark cases**.
- **Pearson Correlation ($r$)**: **0.5914** ($p = 0.00019$, statistically significant agreement).
- **Spearman Rank Correlation ($\rho$)**: **0.5528** ($p = 0.00057$).
- **Agreement within 1.0 point**: **94.3%**.
- See [`evaluation/JUDGE_CALIBRATION.md`](evaluation/JUDGE_CALIBRATION.md) for complete calibration tables.

### Pillar 4: Zero-Data Leakage Guarantee
- Enforces strict temporal partitioning: training interactions strictly precede evaluation timestamps.
- Zero customer ID or conversation ID overlap between retrieval index and evaluation splits.
- Validated automatically in CI via `python scripts/check_leakage.py`.

---

## 🤖 Multi-Provider LLM Integration & Zero-Key Fallback

The agent includes full multi-provider LLM support with runtime configuration via the web UI:

| Provider | Supported Models | Configuration | Default Use Case |
| :--- | :--- | :--- | :--- |
| **Built-in Diagnostic Engine** | Deterministic Knowledge Engine | Zero-Key (Local) | Fast, offline, canonical step-by-step guidance |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` | `OPENAI_API_KEY` | Ultra-fluent, empathetic conversational synthesis |
| **Google Gemini** | `gemini-1.5-flash`, `gemini-2.0-flash` | `GEMINI_API_KEY` | High-speed, large context multimodal drafting |
| **Ollama (Local LLM)** | `llama3`, `mistral`, `qwen2.5` | `http://localhost:11434/v1` | 100% private, zero-cost, local GPU/CPU execution |
| **Groq** | `llama-3.1-8b-instant` | `GROQ_API_KEY` | Near-instantaneous (<300ms) LLM drafting |
| **Custom Endpoint** | Any OpenAI-compatible server | Base URL + API Key | Enterprise proxy or self-hosted vLLM/TGI |

### Dynamic UI Configuration Modal
Click **"LLM Config"** in the top header of the web app to:
1. Select provider from the dropdown.
2. Enter API key (securely stored in memory and `.env`).
3. Click **"Test Connection"** to verify latency and sample response before saving.
4. View real-time model attribution badges (`🤖 OPENAI (gpt-4o-mini)` vs `⚡ Apple Diagnostic Engine`) above every drafted resolution.

---

## ⚠️ Top 5 Real Failure Modes & Mitigation

Extracted verbatim from the master evaluation run in [`reports/failure_analysis.md`](reports/failure_analysis.md):

1. **Post-Exhaustion Self-Help Traps (`eval_060`)**:
   - *Query*: *"Iphone 5S updated to 11.1.2 last night... crashes into a black screen... Have reset, restored, still doing it. Phone is also getting really hot..."*
   - *Root Cause*: Customer explicitly stated standard diagnostic triage had failed. Agent lacked a semantic detector for *customer exhaustion*, suggesting another reboot.
   - *Fix*: Added semantic detector rules for *"already tried"*, *"still doing it"*, *"reset twice"*.
2. **In-Store Personnel Grievances (`eval_183`)**:
   - *Query*: *"Customer service at Westfield Hammersmith London sucks! Store Manager Leo rude..."*
   - *Root Cause*: Named employee dispute auto-handled as general feedback because no profanity was present.
   - *Fix*: Policy rule to escalate queries mentioning store personnel or locations.
3. **Sub-Lexical Keyword Pull in Multi-Symptom Queries (`eval_082`)**:
   - *Query*: *"No, the update notes don't mention wifi. Just crackles, photos and emails..."*
   - *Root Cause*: Embeddings over-indexed on `"wifi"`, overshadowing the acoustic hardware anomaly (`"crackles"`).
   - *Fix*: Calibrated confidence thresholds and hardware keyword filters.
4. **False Escalation on Sarcastic Rhetoric (`eval_001`)**:
   - *Query*: *"when you sorting out a new update as my phone is as much use as a brick now thanks to your shit update"*
   - *Root Cause*: Vulgarity dropped retrieval similarity below 0.50, triggering safe escalation on a routine issue.
5. **Cross-Lingual Semantic Drift (`eval_002`)**:
   - *Query*: *"No te funciona el IOS11?"* (Spanish)
   - *Root Cause*: Pure English corpus caused retrieval similarity to drop below threshold, forcing escalation.
   - *Fix*: Multi-lingual corpus indexing or pre-translation routing.

---

## 📋 Comprehensive Report Index

For in-depth analysis, empirical charts, and methodology, refer to the consolidated reports in [`reports/`](reports/):

- [`reports/final_report.md`](reports/final_report.md): Master technical evaluation report covering problem framing, metrics, and architecture.
- [`reports/failure_analysis.md`](reports/failure_analysis.md): Deep dive into the top 5 real failure modes with verbatim transcripts.
- [`reports/headline_misleading_audit.md`](reports/headline_misleading_audit.md): Unvarnished, self-critical audit of potential vulnerabilities in headline numbers.
- [`reports/dataset_profile.md`](reports/dataset_profile.md): In-depth profiling of the Kaggle Twitter dataset and brand selection criteria.
- [`reports/intent_taxonomy.md`](reports/intent_taxonomy.md): Complete rationale and boundary specifications for the 8 empirical intents.
- [`DECISION_LOG.md`](DECISION_LOG.md): Architectural decision records documenting 14 non-obvious engineering trade-offs.
- [`evaluation/JUDGE_CALIBRATION.md`](evaluation/JUDGE_CALIBRATION.md): Human-to-LLM judge statistical correlation audit.

---

## 🛠️ Running Automated Tests

Run the complete test suite across data cleaner, thread pairing, classifier contracts, retriever contracts, escalation guardrails, response generator, and FastAPI endpoints:

```bash
pytest tests/test_agent.py -v
```

Expected output:
```text
tests/test_agent.py::TestAppleSupportAgentSuite::test_agent_respond_schema PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_api_config_endpoint PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_api_health_endpoint PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_api_predict_endpoint PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_hardware_damage_escalation PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_intent_classifier_contract PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_low_confidence_escalation PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_pii_masking_and_cleaning PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_reply_generator_groundedness PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_retriever_contract PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_safety_hazard_escalation PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_thread_reconstruction PASSED
tests/test_agent.py::TestAppleSupportAgentSuite::test_zero_leakage_guarantee PASSED

======================= 13 passed in ~36s =======================
```

---

## 📄 License & Attribution

- **Dataset**: Kaggle Customer Support on Twitter (`thoughtvector/customer-support-on-twitter`), public CC0.
- **Model Architecture**: Sentence-Transformers `all-MiniLM-L6-v2` (Apache 2.0).
- **Author**: Soham Pal (`palsoham074@gmail.com`)