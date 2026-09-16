"""
Escalation Policy Engine Module
Determines whether to AUTO_HANDLE or ESCALATE with machine reason codes.
Enforces asymmetric cost weighting where routing a hazard to a bot is penalized 5x.
"""

from typing import Dict, Any, Tuple
from agent.policy import PolicyEngine as AgentPolicyEngine

REASON_EXPLANATIONS = {
    "SAFETY_HAZARD_BATTERY_SWELLING": "Critical physical safety hazard detected (swelling/thermal event). Immediate human specialist inspection required.",
    "HARDWARE_PHYSICAL_DAMAGE_GENIUS_BAR": "Physical hardware damage requires hands-on diagnostic inspection and Genius Bar repair.",
    "ACCOUNT_SECURITY_BREACH": "Account compromise, fraudulent charges, or credential theft requires secure human verification.",
    "ACCOUNT_SECURITY_BREACH_ESCALATE": "Account compromise, fraudulent charges, or credential theft requires secure human verification.",
    "HIGH_FRUSTRATION_LEGAL_ESCALATE": "Legal action or formal regulatory complaint keywords detected; routed to tier-2 human supervisor.",
    "LEGAL_THREAT_ESCALATION": "Legal action or formal regulatory complaint keywords detected; routed to tier-2 human supervisor.",
    "LOW_INTENT_CONFIDENCE_ESCALATE": "Intent classification confidence fell below operational threshold; escalating to prevent hallucinated advice.",
    "LOW_RETRIEVAL_SIMILARITY_ESCALATE": "Insufficient historical resolution evidence retrieved; routed to human agent to ensure accuracy.",
    "ROUTINE_AUTO_HANDLE": "High-confidence intent with strong historical evidence and zero escalation triggers."
}

class EscalationPolicy:
    def __init__(self, confidence_threshold: float = 0.58, similarity_threshold: float = 0.50):
        self.underlying = AgentPolicyEngine(
            confidence_threshold=confidence_threshold,
            similarity_threshold=similarity_threshold
        )

    def decide(
        self,
        customer_text: str,
        predicted_intent: str,
        intent_confidence: float,
        top_similarity: float
    ) -> Dict[str, Any]:
        """
        Returns structured decision:
        {
            "decision": "AUTO_HANDLE" | "ESCALATE",
            "confidence": 0.91,
            "reason": "..."
        }
        """
        action, reason_code, meta = self.underlying.evaluate(
            customer_text=customer_text,
            predicted_intent=predicted_intent,
            intent_confidence=intent_confidence,
            top_similarity=top_similarity
        )
        
        decision_str = "ESCALATE" if action == "escalate" else "AUTO_HANDLE"
        explanation = REASON_EXPLANATIONS.get(reason_code, reason_code)
        
        # Calibration of decision confidence
        if decision_str == "ESCALATE":
            # Safety / hardware triggers have high escalation certainty
            if "SAFETY" in reason_code or "HARDWARE" in reason_code:
                dec_conf = 0.98
            else:
                dec_conf = round(max(0.80, 1.0 - intent_confidence), 2)
        else:
            dec_conf = round(min(0.95, (intent_confidence + top_similarity) / 2.0), 2)
            
        return {
            "decision": decision_str,
            "confidence": dec_conf,
            "reason": explanation,
            "reason_code": reason_code
        }

    def evaluate(self, *args, **kwargs):
        return self.underlying.evaluate(*args, **kwargs)
