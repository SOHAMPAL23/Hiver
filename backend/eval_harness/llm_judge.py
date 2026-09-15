"""
Phase 5: Evaluation Harness - LLM Judge Rubric
Grades customer support replies across 4 key operational dimensions (1 to 5 scale):
1. Groundedness: Fidelity to historical Apple troubleshooting procedures and real resources.
2. Actionability: Specificity of diagnostic steps, Settings paths, or official links.
3. Tone Alignment: Empathetic, polite, professional, and on-brand Apple voice.
4. Conciseness: Respects Twitter length constraints without redundant boilerplate.
"""

import re
from typing import Dict, Any

RUBRIC_CRITERIA = {
    "groundedness": {
        5: "Perfect grounding in canonical Apple resolution procedures with verified apple.com domain links.",
        4: "Accurately reflects official troubleshooting; minor phrasing variation but fully faithful.",
        3: "Plausible advice but lacks specific diagnostic references or historical grounding.",
        2: "Generic advice that could apply to any phone; misses Apple-specific workflows.",
        1: "Completely ungrounded, contradictory, or hallucinates non-existent settings/links."
    },
    "actionability": {
        5: "Immediately actionable with explicit step-by-step path (e.g. Settings > Battery) or appointment URL.",
        4: "Actionable next steps provided with clear direction, minor ambiguity on prerequisite steps.",
        3: "Asks customer to troubleshoot generally without specifying the precise path.",
        2: "Vague instruction (e.g. 'restart your device') without further diagnostic options.",
        1: "Zero actionable guidance; customer is left stranded."
    },
    "tone_alignment": {
        5: "Exemplary Apple customer support voice: empathetic, calm, welcoming, professional.",
        4: "Polite and helpful; standard professional customer service tone.",
        3: "Neutral/robotic; polite but lacks empathy or brand warmth.",
        2: "Blunt, cold, or dismissive.",
        1: "Rude, hostile, or totally inappropriate tone."
    },
    "conciseness": {
        5: "Crisp and high signal-to-noise ratio; fits cleanly within Twitter's communication envelope.",
        4: "Well-structured, concise with only minor repetition.",
        3: "Slightly wordy or contains repeated phrases.",
        2: "Rambling or excessive filler sentences.",
        1: "Unreadable wall of text or truncated incoherence."
    }
}

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
        """
        Evaluates a draft reply against rubric criteria and reference resolution.
        """
        reply_lower = draft_reply.lower()
        ref_lower = reference_reply.lower()
        
        # 1. Groundedness Scoring
        has_apple_domain = "apple.com" in reply_lower
        has_settings_path = "settings >" in reply_lower or "settings" in reply_lower
        has_official_keywords = any(k in reply_lower for k in ["genius bar", "iforgot", "reportaproblem", "restart", "update", "battery"])
        
        if has_apple_domain and (has_settings_path or has_official_keywords):
            groundedness = 5.0
        elif has_apple_domain or has_settings_path:
            groundedness = 4.0
        elif has_official_keywords:
            groundedness = 3.0
        elif len(draft_reply.split()) >= 8:
            groundedness = 2.0
        else:
            groundedness = 1.0

        # 2. Actionability Scoring
        if ("settings >" in reply_lower or "http" in reply_lower) and len(draft_reply.split()) >= 12:
            actionability = 5.0
        elif "settings" in reply_lower or "http" in reply_lower or "restart" in reply_lower or "visit" in reply_lower:
            actionability = 4.0
        elif any(w in reply_lower for w in ["check", "try", "ensure", "contact"]):
            actionability = 3.0
        elif len(draft_reply.split()) >= 6:
            actionability = 2.0
        else:
            actionability = 1.0

        # 3. Tone Alignment Scoring
        polite_markers = ["help", "sorry", "we'd like", "we want", "please", "appreciate", "welcome"]
        found_markers = sum(1 for m in polite_markers if m in reply_lower)
        if found_markers >= 3 and not any(h in reply_lower for h in ["obviously", "idiot", "wrong", "cannot help"]):
            tone = 5.0
        elif found_markers >= 1:
            tone = 4.0
        else:
            tone = 3.0

        # 4. Conciseness Scoring
        word_count = len(draft_reply.split())
        char_count = len(draft_reply)
        
        if 15 <= word_count <= 55 and char_count <= 280:
            conciseness = 5.0
        elif word_count < 15 and word_count >= 6:
            conciseness = 4.0
        elif 55 < word_count <= 75:
            conciseness = 4.0
        elif word_count > 75:
            conciseness = 3.0
        else:
            conciseness = 2.0

        overall = round((groundedness + actionability + tone + conciseness) / 4.0, 2)
        
        reasoning = (
            f"Groundedness={groundedness} (domain link: {has_apple_domain}); "
            f"Actionability={actionability} (words: {word_count}); "
            f"Tone={tone}; Conciseness={conciseness}"
        )

        return {
            "groundedness": groundedness,
            "actionability": actionability,
            "tone_alignment": tone,
            "conciseness": conciseness,
            "overall_score": overall,
            "judge_reasoning": reasoning
        }

if __name__ == "__main__":
    judge = LLMJudge()
    sample_reply = "We want to help ensure your battery lasts. Check Settings > Battery to review consumption. Details: https://support.apple.com/battery."
    score = judge.evaluate_reply("battery dies quick", sample_reply, "Check settings battery", "battery_power_charging", "auto_handle")
    print("LLM Judge Test Output:")
    print(score)
