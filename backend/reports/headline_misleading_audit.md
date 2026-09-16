# Audit: What Is Misleading About Our Headline Numbers?

In accordance with the project's foundational principle that *"the proof is worth more than the system"*, this document provides an unvarnished, self-critical deconstruction of our headline results:
- **Headline Intent Macro-F1**: 62.3% (vs. 40.6% Simple Baseline and 2.8% Trivial Baseline)
- **Headline Escalation Recall**: 92.9% (vs. 83.3% Simple Baseline and 0.0% Trivial Baseline)
- **Headline Reply Quality**: 4.57/5.00 (vs. 3.73/5.00 Simple Baseline)

Below are the 6 primary vulnerabilities, structural biases, and statistical nuances that make these headline figures potentially misleading if taken at face value.

---

### 1. The "Hard-Stratified Eval Set" Deflates Apparent Accuracy but Inflates Relative Improvement
- **The Caveat**: In raw production Twitter traffic, `software_update_os_bug` and general complaints constitute $>60\%$ of all incoming volume. A trivial model predicting the majority class would achieve ~40–50% accuracy on natural traffic.
- **Why our 62.3% is misleading**: We deliberately forced a 1:1:1:1:1:1:1:1 balanced distribution (25 examples per class) and heavily over-sampled adversarial edge cases (103 multi-intent, 35 sarcastic, 26 safety hazards, 21 non-English). While this rigorously stress-tests the system, it means our reported macro-F1 represents performance under extreme stress rather than expected day-to-day production accuracy.

---

### 2. High Escalation Recall (92.9%) Conceals Abysmal Escalation Precision (32.5%)
- **The Caveat**: The agent successfully caught 39 out of 42 high-risk customer situations (92.9% recall). However, its precision was only **32.5%**—meaning that for every 3 queries escalated to a human, approximately 2 could have been auto-handled safely.
- **Operational Reality**: In an enterprise support desk, a 32.5% escalation precision would swamp human tier-2 agents with unnecessary queue volume. We deliberately tuned the asymmetric cost matrix ($C_{\text{FAH}} = 5.0$, $C_{\text{FE}} = 1.0$) to prioritize user safety and prevent brand catastrophes (e.g. telling someone with an exploding battery to check their battery health). Presenting 92.9% recall without disclosing the low precision hides a major operational trade-off.

---

### 3. Golden Set Label Noise & Single-Annotator Subjectivity
- **The Caveat**: Ground truth labels in `golden_eval.jsonl` were established by an expert annotator following domain heuristics. Although our two-pass blind audit demonstrated 100% self-consistency across 25 items, this measures *intra-annotator repeatability*, not objective consensus.
- **Vulnerability**: Distinguishing between `software_update_os_bug` and `device_performance_storage` when a customer writes *"Phone is freezing after updating"* has an inherent degree of subjective ambiguity. A second independent human annotator from a different support team might categorize 10–15% of these borderline multi-intent queries differently, which would shift the headline macro-F1 by $\pm 4-6\%$.

---

### 4. Automated Judge Rubric Exhibits "URL-Anchor Confirmation Bias"
- **The Caveat**: Our LLM judge rubric awards high Groundedness (4 or 5) primarily when explicit canonical links (`apple.com/support`, `getsupport.apple.com`, `iforgot.apple.com`) or explicit `Settings >` navigation strings appear in the draft reply.
- **Vulnerability**: Because our Reply Generator was specifically programmed to inject canonical Apple documentation links for each detected intent, it essentially "hacks" the automated rubric's groundedness criteria. A conversational reply that explains a workaround perfectly without citing a URL might receive a 3/5 from the judge despite being more helpful to a mobile user than a cold link.

---

### 5. Distribution Shift: 2017 Twitter Archive vs. Modern Diagnostic Workflows
- **The Caveat**: The Kaggle Twitter dataset captures tweets primarily from late 2017 (the iOS 11 launch era, characterized by the infamous 'I [?]' keyboard glitch and iPhone X release).
- **Vulnerability**: Apple's customer support operating model has evolved significantly. Many troubleshooting paths referenced in historical 2017 tweets (such as iTunes desktop syncing or specific iOS 11 sub-menus) are deprecated in iOS 17/18. Testing on 2017 customer queries proves historical fidelity, but real-world deployment on current customer traffic would suffer distribution shift until the retrieval index is refreshed with modern knowledge base articles.

---

### 6. English Corpus Monolingualism
- **The Caveat**: Although the evaluation set includes non-English edge cases (Spanish/multilingual tweets to @AppleSupport), the retrieval corpus consists of $>98\%$ English agent tweets.
- **Vulnerability**: The agent achieves safety on multilingual queries solely by failing the retrieval similarity threshold and escalating. While safe, claiming multilingual capability would be false: the system cannot effectively resolve non-English inquiries without human routing.
