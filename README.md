# AppleSupport AI Customer Support Agent & Rigorous Evaluation Harness

> **Evaluation-First Take-Home Assignment for Hiver SDE Internship**  
> *"The proof is worth more than the system"* — An honest, self-critical, and reproducible evaluation of an AI support agent grounded in historical resolutions from the Kaggle Twitter Customer Support dataset (`thoughtvector/customer-support-on-twitter`).

---

## Quickstart: Reproduce Headline Results in < 1 Minute

The entire benchmark runs deterministically on local CPU without GPU or API keys:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run master evaluation harness across all 3 systems on the Golden Set
python evaluation/evaluate_all.py

# 3. Run automated test suite
pytest tests/test_agent.py

# 4. Run interactive demonstration
python demo.py
```

*Benchmark execution time: **~19 seconds** on standard CPU.*

---

## 1. Project Overview & Problem Framing

### Selected Brand: `@AppleSupport`
- **Candidate Brand Scoring**: Evaluated across 5 major consumer brands in the Kaggle dataset (`@AppleSupport`, `@AmazonHelp`, `@Uber_Support`, `@Delta`, `@SpotifyCares`). Apple was selected with the highest composite score (**0.9241**) due to its rich technical diagnostic variety (battery degradation, iOS regressions, iCloud authentication) and clear, high-stakes safety boundaries (software self-help vs. battery swelling / Genius Bar repair).
- Run selection script: `python scripts/select_brand.py`.

### What "Good" Means for `@AppleSupport`
1. **Accurate Diagnostic Triage**: Distinguishing hardware anomalies (swelling batteries, cracked screens) from OS update bugs or chemical battery aging.
2. **Strict Grounding in Canonical Procedures**: Never hallucinating diagnostic steps, fake refund policies, or unofficial links. Instructions mirror official Apple documentation (`support.apple.com`, `iforgot.apple.com`, `reportaproblem.apple.com`).
3. **Safety-First Escalation Guardrails**: Intercepting physical hazards (swelling batteries, thermal runaways, sparks) and compromised accounts for human/Genius Bar escalation. Auto-handling must never gamble with user safety.
4. **Empathetic Brand Alignment**: Maintaining Apple's calm, polite, and reassuring customer service voice within Twitter's short-form envelope.

### Deliberate Omissions (What Was Deliberately NOT Built & Why)
- **No Stateful Multi-Turn Dialogue Memory**: Twitter interactions in this dataset are predominantly single-turn public diagnostic triages before redirecting to private DMs. A complex state machine introduces unnecessary latency and failure modes without ground-truth multi-turn telemetry to validate it.
- **No Synthetic Tool Calls / Mock CRM Integrations**: Simulated serial number lookups or mock Genius Bar booking were omitted because synthetic mock tools obscure the core evaluation objective: *honest, rigorous evaluation of model behavior on real data*.
- **No Deep PII Sanitization beyond Regex Scrubbing**: Basic handle, phone, card, and email scrubbing was implemented. Full enterprise NER-based PII redaction was omitted as the public Kaggle dataset had already anonymized customer handles into numeric IDs (`@115854`).

---

## 2. System Architecture

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

## 3. Benchmark Results vs. Baselines

Evaluated on the **200-sample Golden Evaluation Set** (`golden_eval/golden_eval.jsonl` / `data/golden_set.csv`) spanning all 8 empirical intents (25 examples each) with deliberate adversarial stress tests (sarcasm, multi-intent, non-English, safety hazards).

| System | Intent Macro-F1 | Intent Accuracy | Escalation Recall | Escalation Precision | False Auto-Handle (Risk) | Asymmetric Cost / Query | Groundedness (1–5) | Actionability (1–5) | Overall Quality (1–5) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trivial Baseline** *(Majority Class + Static Policy)* | 2.8% | 12.5% | 0.0% | 0.0% | 42 | 1.05 | 3.00 | 4.00 | 4.00 |
| **Simple Baseline** *(TF-IDF + Verbatim Retrieval)* | 40.6% | 41.5% | 83.3% | 79.5% | 7 | 0.22 | 2.27 | 4.21 | 3.73 |
| **AppleSupport Agent** *(Ours: Dense RAG + Guardrails)* | **62.3%** | **63.5%** | **92.9%** | **32.5%** | **3** | **0.48** | **4.53** | **5.00** | **4.57** |

### Key Metric Takeaways
1. **Intent Classification**: The Agent achieves **62.3% Macro-F1**, outperforming the Simple Baseline (40.6%) by **+21.7%** on hard edge cases.
2. **Safety Recall**: The Agent intercepts **92.9% of all high-risk queries** (39/42), dropping critical False Auto-Handles to only 3 (compared to 42 for Trivial and 7 for Simple Baseline).
3. **Escalation Trade-off**: The Agent's Escalation Precision is **32.5%** because the policy engine is intentionally tuned with an asymmetric cost ratio ($C_{\text{FAH}} = 5.0$ vs. $C_{\text{FE}} = 1.0$). In a customer support environment, over-escalating a routine question is mildly inefficient, but auto-handling an exploding battery is catastrophic.
4. **Generation Quality**: Groundedness jumps from **2.27/5** (Simple verbatim retrieval) to **4.53/5** via conditioned synthesis with verified Apple KB anchors.

---

## 4. Human vs. LLM Judge Agreement

To evaluate whether the automated evaluation harness is trustworthy, we calibrated the LLM judge against **35 hand-scored human benchmark cases**:
- **Pearson Correlation ($r$)**: **0.5914** ($p = 0.00019$, statistically significant agreement).
- **Spearman Rank Correlation ($\rho$)**: **0.5528** ($p = 0.00057$).
- **Mean Absolute Difference (MAD)**: **0.4357 points** on a 1–5 scale.
- **Agreement within 0.5 points**: **60.0%**.
- **Agreement within 1.0 point**: **94.3%**.
- Run audit script: `python evaluation/human_vs_llm.py`.

---

## 5. Top 5 Real Failure Modes (Verbatim from Eval Run)

Full analysis documented in [`reports/failure_analysis.md`](reports/failure_analysis.md):

1. **Post-Exhaustion Self-Help Traps (`eval_060`)**:
   - *Query*: *"Iphone 5S updated to 11.1.2 last night. Now when I operate any app... crashes into a black screen with spinning gear. Have reset, restored, still doing it. Phone is also getting really hot..."*
   - *Failure*: Agent classified as `software_update_os_bug` and suggested a forced restart (`auto_handle`).
   - *Hypothesis*: The customer already attempted a reset and full restore. The agent lacked a semantic detector for *customer exhaustion*, offering repetitive advice to an already frustrated user.
2. **In-Store Personnel & Manager Grievances (`eval_183`)**:
   - *Query*: *"Customer service at Westfield Hammersmith London sucks! ... Store Manager Leo rude and defends his staff over customer! ... You lost a customer for life!"*
   - *Failure*: Agent classified as `general_feedback_complaint` and provided an automated web feedback link (`auto_handle`).
   - *Hypothesis*: The customer named a specific store manager. Because no legal threat keywords were used, the policy failed to trigger human escalation for interpersonal store complaints.
3. **Sub-Lexical Keyword Pull in Multi-Symptom Queries (`eval_082`)**:
   - *Query*: *"No, the update notes don't mention wifi. Just crackles, photos and emails. Is there a 11.0.3 coming soon for wifi and battery life fixes?"*
   - *Failure*: Intent misclassified as `connectivity_network_bluetooth` instead of `hardware_physical_damage` / acoustic distortion.
   - *Hypothesis*: Dense embeddings over-indexed on the frequent token `"wifi"`, drowning out the subtle physical acoustic anomaly (`"crackles"`).
4. **False Escalation on Sarcastic Rhetoric (`eval_001`)**:
   - *Query*: *"when you sorting out a new update as my phone is as much use as a brick now thanks to your shit update"*
   - *Failure*: Predicted `software_update_os_bug` but escalated (`false_escalate`).
   - *Hypothesis*: Vulgarity and sarcasm dropped cosine similarity against clinical historical Apple replies below the 0.50 threshold, triggering low-similarity escalation on a routine issue.
5. **Cross-Lingual Semantic Drift (`eval_002`)**:
   - *Query*: *"No te funciona el IOS11?"* (Spanish: "Is iOS 11 not working for you?")
   - *Failure*: Escalated due to low retrieval similarity against English historical corpus.
   - *Hypothesis*: The retrieval corpus lacked dedicated Spanish resolution pairs, forcing safe escalation rather than auto-routing to Spanish Apple documentation (`support.apple.com/es-es`).

---

## 6. What Is Misleading About Our Headline Numbers?

Full audit documented in [`reports/final_report.md`](reports/final_report.md) & [`report/headline_misleading_audit.md`](report/headline_misleading_audit.md):

- **62.3% Macro-F1 Understates Natural Traffic Performance**: On real Twitter streams where 60% of volume is routine iOS update complaints, natural accuracy would be significantly higher. Our benchmark was artificially forced into a 1:1:1:1:1:1:1:1 balanced distribution loaded with adversarial cases.
- **92.9% Escalation Recall Hides 32.5% Escalation Precision**: Catching 93% of hazards comes at the expense of a 67.5% false alarm rate. In production, this would inflate tier-2 human ticket volume unless tuned.
- **Automated Judge Rewards Link Ingestion**: The LLM judge heavily weights the presence of `apple.com` links, which our generator deterministically injects. A concise, empathetic reply without a URL is systematically penalized by the rubric.
- **2017 Dataset Distribution Shift**: Historical tweets refer to iOS 11 and iTunes desktop restore workflows. Modern deployment on iOS 17/18 requires updating the retrieval corpus.

---

## 7. What We'd Do With One More Week (Prioritized)

1. **Semantic Customer Exhaustion Detector (Priority 1)**: Build a dedicated classifier to flag phrases indicating failed prior troubleshooting (*"already tried"*, *"reset three times"*, *"still happening after restore"*), automatically overriding auto-handle policies to human tier-2 routing.
2. **Calibrated Multi-Objective Policy Tuning (Priority 2)**: Perform Pareto-frontier optimization on the confidence/similarity thresholds to elevate escalation precision from 32.5% to $>70\%$ while maintaining $>90\%$ recall on safety hazards.
3. **Multilingual Dual-Corpus Routing (Priority 3)**: Ingest Spanish and French AppleSupport resolution pairs with language detection pre-routing to prevent false escalations on non-English queries.
4. **Human-in-the-Loop Active Learning Pipeline (Priority 4)**: Automatically route low-confidence queries ($0.50 < \text{conf} < 0.65$) to the annotation UI to continuously expand the golden eval set.
5. **Named Entity Recognition for Retail Stores (Priority 5)**: Extract employee names and store locations to escalate interpersonal complaints directly to store leadership.

---

## 8. Running the Backend API & Frontend Dashboard

### Running the API & Interactive Dashboard
Start the FastAPI server:
```bash
python backend/main.py
# Or: uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open your browser at `http://localhost:8000/` to test:
- **Interactive Query Input**: Live classification, decision, and draft reply generation.
- **Historical Evidence View**: Top 3 retrieved customer-brand pairs with similarity scores.
- **Golden Set Explorer**: Select any of the 200 evaluation cases to test model behavior against ground truth.

API Endpoints:
- `POST /predict`: Accepts `{"message": "..."}` and returns structured prediction, decision, reason, reply, and evidence.
- `POST /evaluate`: Returns latest evaluation benchmark metrics.
- `GET /health`: Health check and model readiness status.
- `GET /config`: Active system configuration.

### Running the Human Annotation Tool
```bash
python frontend/annotation_app.py
```
Open `http://localhost:8501/` to review unlabeled tweets, assign empirical intents, select expected actions, document difficulty, and save verified labels directly to `data/golden_set.csv`.

---

## 9. Repository Structure

```
.
├── config.yaml                     # System, brand, data, and policy threshold configuration
├── requirements.txt                # Pinned dependencies
├── .env.example                    # Environment variable template
├── DECISION_LOG.md                 # 14 non-obvious engineering decisions & trade-offs
├── CITATIONS.md                    # Citations for datasets, models, and libraries
├── demo.py                         # Interactive live demonstration script
│
├── data/
│   ├── golden_set.csv              # 200-sample Golden Set with standard tabular schema
│   ├── intent_taxonomy.yaml        # Complete YAML specification of 8 empirical intents
│   └── samples/
│       ├── apple_support_clean.parquet # Clean 20k customer-brand dialogue pairs
│       └── retrieval_corpus.parquet    # Clean 19.8k zero-leakage retrieval index
│
├── src/
│   ├── agent.py                    # Unified AppleSupportAgent (respond and predict APIs)
│   ├── data/
│   │   ├── loader.py               # Dataset loading & subsampling
│   │   ├── cleaner.py              # Text sanitization, PII masking & regex scrubbing
│   │   ├── thread_reconstruction.py# Customer-brand conversation thread pairing
│   │   └── splitter.py             # Temporal and conversation-level partitioning
│   ├── intents/
│   │   ├── taxonomy.py             # Empirical taxonomy specification & boundaries
│   │   └── classifier.py           # Calibrated Logistic Regression on dense embeddings
│   ├── retrieval/
│   │   └── retriever.py            # Cosine vector retrieval over historical resolutions
│   ├── generation/
│   │   └── generator.py            # Retrieval-grounded reply synthesis with Apple KB links
│   └── escalation/
│       └── policy.py               # Auto vs Escalate rule engine with machine reason codes
│
├── backend/
│   └── main.py                     # FastAPI REST API & Interactive UI Dashboard
│
├── frontend/
│   └── annotation_app.py           # Standalone human annotation tool for Golden Set curation
│
├── evaluation/
│   ├── evaluate_all.py             # Master benchmark evaluation runner
│   ├── evaluate_intent.py          # Macro-F1, accuracy, per-class metrics, confusion matrix
│   ├── evaluate_escalation.py      # Precision/recall with asymmetric cost matrix
│   ├── evaluate_replies.py         # Groundedness, actionability, and baseline comparisons
│   ├── llm_judge.py                # 7-axis rubric evaluator (1 to 5 scale)
│   └── human_vs_llm.py             # Human vs LLM judge correlation audit (r=0.5914)
│
├── scripts/
│   ├── explore_dataset.py          # Generates dataset profile report
│   ├── select_brand.py             # Reproducible multi-brand selection benchmark
│   ├── prepare_data.py             # Subsampled data preparation pipeline
│   ├── build_index.py              # Dense vector index verification and build
│   └── check_leakage.py            # Zero-leakage automated audit
│
├── notebooks/
│   └── 01_dataset_exploration.ipynb# Jupyter notebook for exploratory data analysis
│
├── reports/
│   ├── final_report.md             # Comprehensive <= 6-page final evaluation report
│   ├── dataset_profile.md          # Multi-brand volume & message length analysis
│   ├── intent_taxonomy.md          # Rationale and boundaries for every intent
│   └── failure_analysis.md         # Top 5 real failure modes with verbatim examples
│
├── docs/
│   ├── annotation_guidelines.md    # Operating guidelines for human labelers
│   └── architecture.md             # Detailed ASCII architecture diagrams & data flows
│
├── golden_eval/
│   └── golden_eval.jsonl           # 200 hand-curated evaluation instances with metadata
│
├── tests/
│   └── test_agent.py               # 13 automated unit tests covering all system layers
└── eval_results.json               # Serialized benchmark payload for all candidate systems
```

---

## 10. Citations & References

1. **Kaggle Customer Support on Twitter Dataset**:  
   Sriram, S. & Thoughtvector. *Customer Support on Twitter*. Kaggle Datasets (2017). Available at `thoughtvector/customer-support-on-twitter`.
2. **Dense Sentence Embeddings (`all-MiniLM-L6-v2`)**:  
   Wang, K., Reimers, N., et al. *MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers*. NeurIPS 2020.
3. **Calibrated Probability Modeling**:  
   Niculescu-Mizil, A., & Caruana, R. *Predicting good probabilities with supervised learning*. ICML 2005.
4. **Scikit-Learn**:  
   Pedregosa et al. *Scikit-learn: Machine Learning in Python*. JMLR 12, pp. 2825-2830 (2011).
5. **FastAPI**:  
   Ramírez, S. *FastAPI: Modern, fast Web framework for building APIs with Python*. (2018).
#   H i v e r  
 