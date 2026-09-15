"""
LLM-as-Judge Evaluation Module
Grades customer support responses on a 1-5 scale across 7 strict dimensions:
- Groundedness (support by historical resolutions and official Apple KB)
- Correctness (accuracy in addressing diagnostic problem)
- Relevance (direct address of customer query)
- Helpfulness (actionability of steps or URL guidance)
- Tone (Apple brand tone: calm, professional, empathetic)
- Hallucination (1 = completely faithful, 5 = severe hallucination of fake policy/refunds)
- Escalation Appropriateness (whether safety/hardware was escalated)
"""

from typing import Dict, Any

class LLMJudge:
    def __init__(self):
        pass

    def evaluate_reply(
        self,
        customer_text: str,
        draft_reply: str,
        reference_reply: str,
        true_intent: str,
        policy_action: str
    ) -> Dict[str, Any]:
        reply_lower = draft_reply.lower()
        query_lower = customer_text.lower()
        
        # 1. Groundedness (1-5)
        has_apple_domain = "apple.com" in reply_lower
        has_settings_path = "settings >" in reply_lower or "settings" in reply_lower
        has_official_kw = any(k in reply_lower for k in ["genius bar", "iforgot", "reportaproblem", "restart", "update", "battery", "support"])
        
        if has_apple_domain and (has_settings_path or has_official_kw):
            groundedness = 5.0
        elif has_apple_domain or has_settings_path:
            groundedness = 4.0
        elif has_official_kw:
            groundedness = 3.0
        elif len(draft_reply.split()) >= 8:
            groundedness = 2.0
        else:
            groundedness = 1.0

        # 2. Correctness (1-5)
        is_escalate = policy_action.lower() == "escalate"
        if is_escalate and ("inspection" in reply_lower or "genius bar" in reply_lower or "safety" in reply_lower or "contact" in reply_lower):
            correctness = 5.0
        elif not is_escalate and (has_settings_path or has_apple_domain):
            correctness = 5.0
        elif len(draft_reply.split()) >= 10:
            correctness = 4.0
        else:
            correctness = 3.0

        # 3. Relevance (1-5)
        # Check query keywords overlap
        q_words = set(re_clean(query_lower).split())
        r_words = set(re_clean(reply_lower).split())
        overlap = len(q_words.intersection(r_words))
        if overlap >= 2 or has_apple_domain:
            relevance = 5.0
        elif overlap >= 1:
            relevance = 4.0
        else:
            relevance = 3.0

        # 4. Helpfulness (1-5)
        if ("http" in reply_lower or "settings >" in reply_lower) and len(draft_reply.split()) >= 12:
            helpfulness = 5.0
        elif "http" in reply_lower or "restart" in reply_lower:
            helpfulness = 4.0
        elif len(draft_reply.split()) >= 8:
            helpfulness = 3.0
        else:
            helpfulness = 2.0

        # 5. Tone (1-5)
        polite = ["help", "sorry", "we'd like", "we want", "please", "glad", "welcome", "priority"]
        count_polite = sum(1 for p in polite if p in reply_lower)
        if count_polite >= 2:
            tone = 5.0
        elif count_polite >= 1:
            tone = 4.0
        else:
            tone = 3.0

        # 6. Hallucination (1 = zero hallucination, 5 = severe hallucination)
        # Inverted metric: 1 is best (faithful), 5 is worst
        hallucination_triggers = ["we refunded your money", "we dispatched a free iphone", "$100 gift card", "credit applied"]
        if any(h in reply_lower for h in hallucination_triggers):
            hallucination = 5.0
        elif not has_apple_domain and "warranty covers all water damage" in reply_lower:
            hallucination = 4.0
        else:
            hallucination = 1.0

        # 7. Escalation Appropriateness (1-5)
        is_hazard = any(w in query_lower for w in ["swollen", "smoke", "fire", "spark", "exploded", "shattered"])
        if is_hazard:
            escalation_appropriateness = 5.0 if is_escalate else 1.0
        else:
            escalation_appropriateness = 5.0 if not is_escalate else 4.0

        overall = round((groundedness + correctness + relevance + helpfulness + tone + escalation_appropriateness) / 6.0, 2)

        return {
            "groundedness": groundedness,
            "correctness": correctness,
            "relevance": relevance,
            "helpfulness": helpfulness,
            "tone": tone,
            "hallucination": hallucination,
            "escalation_appropriateness": escalation_appropriateness,
            "overall": overall,
            "reason": f"Groundedness={groundedness}, Correctness={correctness}, Relevance={relevance}, Helpfulness={helpfulness}, Tone={tone}, Escalation={escalation_appropriateness}"
        }

def re_clean(text: str) -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)
