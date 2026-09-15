"""
Phase 3: Trivial Baseline
1. Predicts majority class intent ('software_update_os_bug').
2. Returns a static canned template.
3. Policy: Always auto-handle (or static default).
Sets the absolute performance floor for comparison.
"""

from typing import Dict, Any

CANNED_REPLIES = {
    "software_update_os_bug": "Thank you for reaching out to Apple Support. Please restart your device and ensure you are on the latest software version.",
    "battery_power_charging": "Thank you for reaching out to Apple Support. Please check Settings > Battery for diagnostic info.",
    "account_apple_id_icloud": "Thank you for reaching out to Apple Support. Please visit iforgot.apple.com to reset your credentials.",
    "hardware_physical_damage": "Thank you for reaching out to Apple Support. Please visit an Apple Store Genius Bar for hardware assistance.",
    "connectivity_network_bluetooth": "Thank you for reaching out to Apple Support. Please try resetting your network settings.",
    "billing_subscriptions_appstore": "Thank you for reaching out to Apple Support. Please check reportaproblem.apple.com for billing queries.",
    "device_performance_storage": "Thank you for reaching out to Apple Support. Please check Settings > General > iPhone Storage.",
    "general_feedback_complaint": "Thank you for reaching out to Apple Support. We appreciate your feedback and apologize for any inconvenience."
}

class TrivialBaseline:
    def __init__(self, majority_intent: str = "software_update_os_bug", default_policy: str = "auto_handle"):
        self.majority_intent = majority_intent
        self.default_policy = default_policy

    def predict(self, customer_text: str) -> Dict[str, Any]:
        intent = self.majority_intent
        reply = CANNED_REPLIES.get(intent, "Thank you for reaching out to Apple Support.")
        action = self.default_policy
        reason = "TRIVIAL_BASELINE_STATIC_POLICY"
        
        return {
            "predicted_intent": intent,
            "intent_confidence": 0.125,  # 1/8 chance
            "draft_reply": reply,
            "retrieval_similarity": 0.0,
            "policy_action": action,
            "policy_reason": reason,
            "model_type": "trivial_majority"
        }

if __name__ == "__main__":
    baseline = TrivialBaseline()
    res = baseline.predict("My iPhone battery is dying so fast!")
    print("Trivial Baseline Sample Output:")
    print(res)
