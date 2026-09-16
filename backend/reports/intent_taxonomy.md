# Empirical Intent Taxonomy for @AppleSupport

This taxonomy was derived empirically from clustering 1,500 customer queries using KMeans ($k=8$) and dense `all-MiniLM-L6-v2` embeddings over the Twitter Customer Support dataset, rather than adopting generic SaaS schemas like Banking77.

---

## 1. `software_update_os_bug`
- **Why it exists**: Major iOS releases (such as iOS 11 during the dataset timeframe) generate massive surges of user inquiries regarding post-update freezes, boot loops, and app crashing.
- **Description**: Technical issues arising after iOS or macOS software updates, including system crashes, reboot loops, UI freezing, or OS-level regression bugs.
- **Decision Boundary**: Focuses strictly on OS-level anomalies caused by system updates. If the issue is solely battery draining after an update, it is categorized as `battery_power_charging`.
- **Escalation Policy**: Routine diagnostics (force restart, recovery mode restore) are Auto-Handled. Repeated boot-loops requiring hardware inspection are Escalated.

## 2. `battery_power_charging`
- **Why it exists**: Battery health degradation, rapid discharge, and cable charging anomalies represent ~25% of all inbound Apple hardware queries.
- **Description**: Rapid battery percentage drain, overheating during charging or normal use, lightning cable failure, or battery health degradation.
- **Decision Boundary**: Covers physical charging cables/ports and chemical battery discharge. If a battery has physically swollen and bent the phone frame, it is immediately routed to `hardware_physical_damage` and Escalated.
- **Escalation Policy**: Standard battery optimization tips are Auto-Handled. Thermal events or physical swelling are Critical Safety Escalations.

## 3. `account_apple_id_icloud`
- **Why it exists**: Account credentials, two-factor authentication lockouts, and iCloud sync issues are high-friction customer touchpoints that can lock users out of their devices.
- **Description**: Apple ID authentication, forgotten passwords, two-factor authentication (2FA) lockouts, iCloud storage sync, or suspicious account access.
- **Decision Boundary**: Covers identity authentication and iCloud data sync. If the inquiry relates to an unauthorized billing charge, it is classified as `app_store_billing_purchase`.
- **Escalation Policy**: Standard self-help links (`iforgot.apple.com`) are Auto-Handled. Compromised or hacked accounts are immediately Escalated.

## 4. `hardware_physical_damage`
- **Why it exists**: Physical device trauma (broken screens, water ingress, chassis bends) cannot be diagnosed or solved via social media troubleshooting and must be routed to Genius Bar service.
- **Description**: Cracked screens, broken glass, water/liquid ingress, swelling batteries, malfunctioning physical buttons, or Genius Bar hardware repair requests.
- **Decision Boundary**: Covers all physical structural damage and component failure.
- **Escalation Policy**: Strictly 100% Escalated to Genius Bar appointment routing (`getsupport.apple.com`). Never auto-handle hardware repair promises.

## 5. `connectivity_network_bluetooth`
- **Why it exists**: Seamless connectivity across Apple ecosystem products (AirPods, Apple Watch, Wi-Fi networks, cellular SIMs) is essential to daily device utility.
- **Description**: Cellular data reception dropouts, Wi-Fi disconnection/slow speeds, Bluetooth pairing failures (AirPods, Apple Watch), or carrier SIM errors.
- **Decision Boundary**: Focuses on radio connectivity. If audio crackling occurs over Bluetooth, verify whether it is connectivity or acoustic speaker hardware.
- **Escalation Policy**: Network settings reset instructions are Auto-Handled. Suspected cellular modem baseband hardware failure is Escalated.

## 6. `audio_sound_microphone`
- **Why it exists**: Ear speaker failure, microphone obstruction, and speaker crackling represent distinct acoustic hardware/software diagnostics that frustrate call usability.
- **Description**: Crackling or distorted speaker audio, microphone not picking up voice on calls, receiver volume too low, or headphone jack/Lightning adapter audio issues.
- **Decision Boundary**: Audio distortion and microphone pickup. If AirPods disconnect completely, label `connectivity_network_bluetooth`.
- **Escalation Policy**: Audio cleaning and settings checks are Auto-Handled. Blown speakers are Escalated to Genius Bar.

## 7. `app_store_billing_purchase`
- **Why it exists**: Financial disputes involving subscription renewals, double charges, and accidental in-app purchases carry high customer anxiety and strict regulatory compliance mandates.
- **Description**: Unauthorized App Store or iTunes charges, subscription cancellation requests, double charges, payment method declines, or in-app purchase refund disputes.
- **Decision Boundary**: Focuses on payment transactions and subscriptions.
- **Escalation Policy**: Standard refund portal guidance (`reportaproblem.apple.com`) is Auto-Handled. Contested unauthorized fraud charges are Escalated.

## 8. `general_feedback_complaint`
- **Why it exists**: Customers regularly use public Twitter to vent frustration about pricing, executive decisions, or retail store employee interactions that require brand reputation management.
- **Description**: General complaints about Apple policies, retail store personnel grievances, shipping/order delays, feedback on product features, or sarcasm/rants without specific technical diagnostics.
- **Decision Boundary**: Subjective feedback and personnel grievances.
- **Escalation Policy**: General policy suggestions are Auto-Handled with feedback links (`apple.com/feedback`). Complaints naming specific employees or retail store managers are Escalated.
