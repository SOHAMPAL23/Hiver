"""
Phase 4: Unified Agent Pipeline
Integrates IntentClassifier, HistoricalResolutionRetriever, PolicyEngine,
and ReplyGenerator into a single, clean, production-grade interface.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Any
from agent.classifier import IntentClassifier
from agent.retriever import HistoricalResolutionRetriever
from agent.policy import PolicyEngine
from agent.generator import ReplyGenerator

class AppleSupportAgent:
    def __init__(self):
        print("[*] Initializing AppleSupportAgent pipeline components...")
        self.classifier = IntentClassifier()
        self.retriever = HistoricalResolutionRetriever()
        self.policy = PolicyEngine()
        self.generator = ReplyGenerator()
        print("[OK] AppleSupportAgent successfully initialized.")

    def predict(self, customer_text: str) -> Dict[str, Any]:
        # 1. Intent Classification
        predicted_intent, confidence, prob_dict = self.classifier.predict(customer_text)

        # 2. Historical Retrieval
        retrieved_items = self.retriever.retrieve(customer_text, top_k=3)
        top_sim = retrieved_items[0]['similarity_score'] if retrieved_items else 0.0

        # 3. Policy Guardrails & Escalation Decision
        action, reason, policy_meta = self.policy.evaluate(
            customer_text=customer_text,
            predicted_intent=predicted_intent,
            intent_confidence=confidence,
            top_similarity=top_sim
        )

        # 4. Retrieval-Grounded Reply Drafting
        reply = self.generator.generate_reply(
            customer_text=customer_text,
            predicted_intent=predicted_intent,
            policy_action=action,
            policy_reason=reason,
            retrieved_resolutions=retrieved_items
        )

        return {
            "predicted_intent": predicted_intent,
            "intent_confidence": confidence,
            "all_intent_probabilities": prob_dict,
            "retrieval_similarity": top_sim,
            "retrieved_historical_resolutions": retrieved_items,
            "policy_action": action,
            "policy_reason": reason,
            "policy_metadata": policy_meta,
            "draft_reply": reply,
            "model_type": "embedding_dense_rag_agent"
        }

if __name__ == "__main__":
    agent = AppleSupportAgent()
    samples = [
        "My iPhone 7 battery is draining 50% in an hour after iOS 11 update",
        "Dropped my phone on concrete and the back glass is cracked into pieces",
        "I was charged twice for Apple Music subscription this month. Need refund",
        "Hello can someone help me"
    ]
    for s in samples:
        res = agent.predict(s)
        print(f"\n--- Customer Query: '{s}' ---")
        print(f"Intent: {res['predicted_intent']} (Conf: {res['intent_confidence']:.2f})")
        print(f"Action: {res['policy_action']} | Reason: {res['policy_reason']}")
        print(f"Top Similarity: {res['retrieval_similarity']:.2f}")
        print(f"Draft Reply: {res['draft_reply']}")
