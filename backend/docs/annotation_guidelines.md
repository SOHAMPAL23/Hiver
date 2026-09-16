# Annotation Guidelines: AppleSupport Golden Evaluation Benchmark

These guidelines provide standard operating procedures for human annotators curating and labeling evaluation instances for the AppleSupport AI Agent.

---

## 1. Intent Classification Guidelines

Annotators must assign exactly one primary intent from the 8 empirical classes:

1. `software_update_os_bug`: Post-update anomalies, app crashes, boot loops, system freezing.
2. `battery_power_charging`: Battery drain, overheating, cable charging failures, battery health.
3. `account_apple_id_icloud`: Apple ID logins, 2FA codes, password resets, iCloud data sync.
4. `hardware_physical_damage`: Cracked glass, water damage, chassis deformation, swollen battery.
5. `connectivity_network_bluetooth`: Cellular dropouts, Wi-Fi errors, Bluetooth pairing (AirPods/Watch).
6. `audio_sound_microphone`: Speaker crackle, microphone silence, low receiver volume.
7. `app_store_billing_purchase`: Unauthorized charges, subscription refunds, App Store purchase disputes.
8. `general_feedback_complaint`: Store personnel complaints, feedback, order shipping status.

---

## 2. Handling Edge Cases & Complex Queries

### A. Ambiguous & Multi-Intent Messages
- If a customer mentions both an iOS update and rapid battery drain:
  - Label as `battery_power_charging` if the primary symptom requiring action is battery degradation.
  - Label as `software_update_os_bug` if the complaint is primarily that the update broke the operating system.
  - Document secondary intent in metadata.

### B. Unclear Messages / Insufficient Context
- Example: *"Help my phone is broken"* or *"It's not working"*.
- **Action**: Assign `general_feedback_complaint` or the most probable hardware/software class.
- **Policy**: Mark expected action as `escalate` or prompt for clarification, because an automated diagnostic reply cannot safely address an unspecified problem.

### C. Abusive / Sarcastic / Emotional Messages
- Profanity and sarcasm must **not** change the underlying technical diagnosis.
- Example: *"when you sorting out a new update as my phone is as much use as a brick now thanks to your shit update"* -> Intent is `software_update_os_bug`.
- If vulgarity indicates extreme customer frustration, note whether human intervention is required to de-escalate.

### D. Account-Specific Information Requests
- Any request requiring access to private user records (e.g. *"Look up my Apple ID order #987654"*, *"Why was my card charged?"*) must be flagged for `escalate` (or self-service portal `reportaproblem.apple.com`).
- The agent must never claim to have looked up an account or promise that an action has been completed.

### E. Physical Safety Hazards & Battery Swelling
- **CRITICAL ZERO-TOLERANCE RULE**: Any mention of swollen batteries, bulging casings, smoke, sparks, or intense burning heat must be marked as `escalate` with reason `SAFETY_HAZARD_BATTERY_SWELLING`.
- Auto-handling a physical safety hazard is penalized 5x in operational benchmarks.

### F. Legal Threats & Formal Disputes
- Keywords like `"lawyer"`, `"attorney"`, `"sue"`, `"court"`, or `"police"` must be marked `escalate` with reason `LEGAL_THREAT_ESCALATION`.
