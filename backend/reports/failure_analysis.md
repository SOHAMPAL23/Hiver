# Comprehensive Failure Analysis: Top 5 Real Failure Modes

Extracted verbatim from the master evaluation run on the 200-sample Golden Evaluation Set (`eval_results.json`).

---

### Failure Mode 1: Post-Exhaustion Self-Help Traps (False Auto-Handle)
- **Evaluation ID**: `eval_060`
- **Customer Query**: 
  > *"Iphone 5S updated to 11.1.2 last night. Now when I operate any app (including settings)it crashes into a black screen with spinning gear. Have reset, restored, still doing it. Phone is also getting really hot. Seems to also be waking itself 2 passcode screen radomly"*
- **Ground Truth**: `software_update_os_bug` | Action: `escalate` (`EXHAUSTED_SELF_HELP_RESTORATION`)
- **Agent Output**: Intent: `software_update_os_bug` (Conf: 0.81) | Action: `auto_handle` (`ROUTINE_AUTO_HANDLE`)
- **Draft Reply Emitted**: *"We want to help ensure your device runs smoothly after updating. What specific device and iOS version are you running? Try a forced restart, or review our update troubleshooting guide: https://support.apple.com/ios/update"*
- **Root Cause & Hypothesis**: The agent classified the query into `software_update_os_bug` with high confidence because of tokens like `"updated to 11.1.2"` and `"crashes"`. However, the customer explicitly stated they *already* did a reset and full restore (`"Have reset, restored, still doing it"`). A human agent immediately recognizes that standard diagnostic triage is exhausted and the customer requires escalated diagnostic hardware repair or tier-2 support. The stateless agent lacked a semantic detector for *customer exhaustion*.
- **Potential Fix**: Implement a customer exhaustion regex/embedding classifier (phrases: `"already tried"`, `"reset twice"`, `"still doing it"`) that forces an escalation override.

---

### Failure Mode 2: In-Store Personnel & Manager Complaints (False Auto-Handle)
- **Evaluation ID**: `eval_183`
- **Customer Query**: 
  > *"Customer service at Westfield Hammersmith London sucks! Has helped decide that my next phone will not be . Store Manager Leo rude and defends his staff over customer! Great one Apple. You lost a customer for life!"*
- **Ground Truth**: `general_feedback_complaint` | Action: `escalate` (`HIGH_FRUSTRATION_HUMAN_ATTENTION`)
- **Agent Output**: Intent: `general_feedback_complaint` (Conf: 0.77) | Action: `auto_handle` (`ROUTINE_AUTO_HANDLE`)
- **Draft Reply Emitted**: *"We appreciate your feedback and want to make sure your Apple experience meets our highest standards. You can share your suggestions directly with our product teams at https://www.apple.com/feedback."*
- **Root Cause & Hypothesis**: The agent identified the complaint intent, but because the customer did not use explicit legal keywords (`"lawyer"`, `"sue"`), the policy engine defaulted to standard feedback self-service. Sending an automated web link to an irate customer who just named a specific retail store manager (`"Store Manager Leo"`) is a known enterprise customer support catastrophe. The sentiment threshold needs named-entity and interpersonal grievance sensitivity.
- **Potential Fix**: Add Named Entity Recognition (NER) for retail staff titles (`"Store Manager"`, `"Genius"`, `"employee"`) and route interpersonal grievances directly to human customer relations.

---

### Failure Mode 3: Sub-Lexical Keyword Pull in Multi-Symptom Queries (Intent Mismatch)
- **Evaluation ID**: `eval_082`
- **Customer Query**: 
  > *"No, the update notes don't mention wifi. Just crackles, photos and emails. Is there a 11.0.3 coming soon for wifi and battery life fixes?"*
- **Ground Truth**: `hardware_physical_damage` (or `audio_sound_microphone`) | Action: `escalate`
- **Agent Output**: Intent: `connectivity_network_bluetooth` (Conf: 0.69) | Action: `auto_handle` (`ROUTINE_AUTO_HANDLE`)
- **Draft Reply Emitted**: *"Let's get you connected. Try restarting your device and resetting network settings via Settings > General > Reset > Reset Network Settings. Details: https://support.apple.com/HT204051"*
- **Root Cause & Hypothesis**: The customer mentions three distinct domains: audio hardware speaker artifacts (`"crackles"`), connectivity (`"wifi"`), and power (`"battery life fixes"`). The dense embedding model weighted the explicit token `"wifi"` higher than the subtle acoustic distortion term `"crackles"`, misrouting the primary diagnosis and offering network reset advice for what was fundamentally an OS firmware release cycle inquiry with physical acoustic symptoms.
- **Potential Fix**: Use multi-intent tagging with symptom hierarchy where physical hardware anomalies take precedence over connectivity.

---

### Failure Mode 4: False Escalation on Sarcastic Rhetoric (False Escalate)
- **Evaluation ID**: `eval_001`
- **Customer Query**: 
  > *"when you sorting out a new update as my phone is as much use as a brick now thanks to your shit update"*
- **Ground Truth**: `software_update_os_bug` | Action: `auto_handle` (`POST_UPDATE_RECOVERY_TRIAGE`)
- **Agent Output**: Intent: `software_update_os_bug` (Conf: 0.64) | Action: `escalate` (`LOW_RETRIEVAL_SIMILARITY_ESCALATE`)
- **Draft Reply Emitted**: *"We want to ensure you get the exact help you need for this issue. We are connecting you with a dedicated Apple Support specialist who can look into your specific setup: https://support.apple.com/ios/update."*
- **Root Cause & Hypothesis**: The customer used hyperbole (`"brick"`) and vulgarity (`"shit update"`). While the technical issue is a standard post-update regression, the vulgar phrasing caused the semantic similarity against official historical Apple resolutions (which are uniformly polite and clinical) to drop below the `0.50` retrieval similarity threshold. This triggered the low retrieval guardrail, unnecessarily escalating a routine recovery triage question.
- **Potential Fix**: Pre-process text to strip profanity and rhetorical hyperbole before computing retrieval similarity against clinical brand corpora.

---

### Failure Mode 5: Cross-Lingual Semantic Drift (False Escalate)
- **Evaluation ID**: `eval_002`
- **Customer Query**: 
  > *"No te funciona el IOS11?"* (Translation: "Is iOS 11 not working for you?")
- **Ground Truth**: `software_update_os_bug` | Action: `auto_handle`
- **Agent Output**: Intent: `software_update_os_bug` (Conf: 0.61) | Action: `escalate` (`LOW_RETRIEVAL_SIMILARITY_ESCALATE`)
- **Draft Reply Emitted**: *"We want to ensure you get the exact help you need for this issue. We are connecting you with a dedicated Apple Support specialist who can look into your specific setup: https://support.apple.com/ios/update."*
- **Root Cause & Hypothesis**: While `all-MiniLM-L6-v2` has moderate multilingual capacity, our retrieval index was predominantly populated by English AppleSupport tweets. Consequently, non-English queries rarely achieve $>0.50$ cosine similarity with English brand replies. The system safely escalated, but failed to auto-respond with Apple's standard Spanish support portal link (`https://support.apple.com/es-es`).
- **Potential Fix**: Add an upfront language identification stage that routes Spanish, French, and German queries to language-specific knowledge base anchors.
