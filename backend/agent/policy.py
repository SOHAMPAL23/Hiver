"""
Phase 4: Agent Component - Auto-Handle vs Escalate Policy Engine
Evaluates intent confidence, retrieval similarity, safety hazards, hardware damage,
and security indicators to decide whether the agent should auto-reply or route to human.
Always emits a machine-readable policy reason code.
"""

from typing import Dict, Any, Tuple

CONFIDENCE_THRESHOLD = 0.58
SIMILARITY_THRESHOLD = 0.50

SAFETY_PATTERNS = [
    "swollen", "swelled", "bulging", "smoke", "smoking", "spark", "sparking",
    "fire", "exploded", "burning smell", "hot to touch"
]

HARDWARE_DAMAGE_PATTERNS = [
    "shattered", "cracked screen", "broken glass", "cracked back", "water damage",
    "dropped in water", "screen replacement", "physical repair", "broken display"
]

SECURITY_PATTERNS = [
    "hacked", "stolen", "unauthorized charge", "someone accessed", "scam",
    "fraudulent", "compromised account"
]

FRUSTRATION_LEGAL_PATTERNS = [
    "lawyer", "sue", "legal action", "attorney", "court", "unacceptable fraud",
    "consumer protection", "police"
]

class PolicyEngine:
    def __init__(
        self,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ):
        self.confidence_threshold = confidence_threshold
        self.similarity_threshold = similarity_threshold

    def evaluate(
        self,
        customer_text: str,
        predicted_intent: str,
        intent_confidence: float,
        top_similarity: float
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Returns (action, reason_code, diagnostic_metadata)
        Action is either 'auto_handle' or 'escalate'
        """
        t_lower = customer_text.lower()
        metadata = {
            "confidence": intent_confidence,
            "top_similarity": top_similarity,
            "rule_triggered": None
        }

        # 1. Critical Physical Safety Hazards (Highest Priority - Never Auto-Handle)
        for pattern in SAFETY_PATTERNS:
            if pattern in t_lower:
                reason = "SAFETY_HAZARD_BATTERY_SWELLING"
                metadata["rule_triggered"] = f"safety:{pattern}"
                return "escalate", reason, metadata

        # 2. Hardware Physical Damage (Requires Certified In-Person Inspection)
        screen_feature_patterns = [
            "screenshot", "screen shot", "screen recording", "screen record",
            "screen time", "screen brightness", "home screen", "lock screen",
            "split screen", "screen mirror", "screen share"
        ]
        is_screen_feature = any(p in t_lower for p in screen_feature_patterns)

        for pattern in HARDWARE_DAMAGE_PATTERNS:
            if pattern in t_lower:
                reason = "HARDWARE_PHYSICAL_DAMAGE_GENIUS_BAR"
                metadata["rule_triggered"] = f"hardware:{pattern}"
                return "escalate", reason, metadata

        if predicted_intent == "hardware_physical_damage" and not is_screen_feature:
            reason = "HARDWARE_PHYSICAL_DAMAGE_GENIUS_BAR"
            metadata["rule_triggered"] = "intent:hardware_physical_damage"
            return "escalate", reason, metadata

        # 3. Account Security & Compromise (Requires Identity Verification)
        for pattern in SECURITY_PATTERNS:
            if pattern in t_lower:
                reason = "ACCOUNT_SECURITY_BREACH_ESCALATE"
                metadata["rule_triggered"] = f"security:{pattern}"
                return "escalate", reason, metadata

        # 4. Hostile Customer Venting or Legal Threats
        for pattern in FRUSTRATION_LEGAL_PATTERNS:
            if pattern in t_lower:
                reason = "HIGH_FRUSTRATION_LEGAL_ESCALATE"
                metadata["rule_triggered"] = f"legal:{pattern}"
                return "escalate", reason, metadata

        # 5. Low Intent Confidence Guardrail
        if intent_confidence < self.confidence_threshold:
            reason = "LOW_INTENT_CONFIDENCE_ESCALATE"
            metadata["rule_triggered"] = f"conf:{intent_confidence:.2f}<{self.confidence_threshold}"
            return "escalate", reason, metadata

        # 6. Low Retrieval Similarity Guardrail (Out-of-Domain or Unprecedented Query)
        if top_similarity < self.similarity_threshold:
            reason = "LOW_RETRIEVAL_SIMILARITY_ESCALATE"
            metadata["rule_triggered"] = f"sim:{top_similarity:.2f}<{self.similarity_threshold}"
            return "escalate", reason, metadata

        # 7. Safe Auto-Handle with Verified Triage Grounding
        reason = f"ROUTINE_AUTO_HANDLE_{predicted_intent.upper()}"
        metadata["rule_triggered"] = "passed_all_guardrails"
        return "auto_handle", reason, metadata

if __name__ == "__main__":
    engine = PolicyEngine()
    print(engine.evaluate("My battery is swelling and cracked the screen!", "battery_power_charging", 0.95, 0.85))
    print(engine.evaluate("How do I update to iOS 11?", "software_update_os_bug", 0.92, 0.78))
    print(engine.evaluate("asdf qwerty 123", "general_feedback_complaint", 0.35, 0.22))
