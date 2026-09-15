"""
End-to-End Customer Support Agent
Provides unified interface: agent.respond(customer_message)
Produces inspectable output schema with intent, decision, evidence, and grounded reply.
"""

import os
from typing import Dict, Any, List, Optional
from src.intents.classifier import IntentClassifier
from src.retrieval.retriever import HistoricalRetriever
from src.escalation.policy import EscalationPolicy
from src.generation.generator import ReplyGenerator

class AppleSupportAgent:
    def __init__(
        self,
        classifier_model_path: str = "models/classifier_model.pkl",
        retrieval_index_path: str = "models/retrieval_index.npz",
        confidence_threshold: float = 0.58,
        similarity_threshold: float = 0.50
    ):
        print("[*] Initializing End-to-End AppleSupportAgent...")
        # Resolve artifact paths with fallback to agent/
        if not os.path.exists(classifier_model_path) and os.path.exists("agent/classifier_model.pkl"):
            classifier_model_path = "agent/classifier_model.pkl"
        if not os.path.exists(retrieval_index_path) and os.path.exists("agent/retrieval_index.npz"):
            retrieval_index_path = "agent/retrieval_index.npz"

        self.classifier = IntentClassifier(model_path=classifier_model_path)
        self.retriever = HistoricalRetriever(index_path=retrieval_index_path)
        self.policy = EscalationPolicy(
            confidence_threshold=confidence_threshold,
            similarity_threshold=similarity_threshold
        )
        self.generator = ReplyGenerator()
        print("[OK] AppleSupportAgent successfully ready for production inference.")

    def respond(self, customer_message: str) -> Dict[str, Any]:
        """
        Unified response method matching Section 14 specification.
        """
        # 1. Intent Classification
        clf_result = self.classifier.classify(customer_message)
        intent = clf_result["intent"]
        intent_conf = clf_result["confidence"]

        # 2. Historical Retrieval
        ret_result = self.retriever.retrieve(customer_message, top_k=3)
        retrieved_examples = ret_result.get("retrieved_examples", [])
        top_sim = retrieved_examples[0]["similarity"] if retrieved_examples else 0.0

        # 3. Escalation Decision
        policy_res = self.policy.decide(
            customer_text=customer_message,
            predicted_intent=intent,
            intent_confidence=intent_conf,
            top_similarity=top_sim
        )
        decision = policy_res["decision"]
        decision_conf = policy_res["confidence"]
        escalation_reason = policy_res["reason"] if decision == "ESCALATE" else None

        # 4. Response Generation
        raw_retrieval_format = [
            {
                "customer_query": ex["customer_message"],
                "historical_reply": ex["historical_response"],
                "similarity_score": ex["similarity"]
            }
            for ex in retrieved_examples
        ]
        
        reply = self.generator.generate(
            customer_text=customer_message,
            predicted_intent=intent,
            policy_action="escalate" if decision == "ESCALATE" else "auto_handle",
            policy_reason=policy_res.get("reason_code", "ROUTINE_AUTO_HANDLE"),
            retrieved_resolutions=raw_retrieval_format
        )

        return {
            "intent": intent,
            "intent_confidence": intent_conf,
            "decision": decision,
            "decision_confidence": decision_conf,
            "escalation_reason": escalation_reason,
            "reply": reply,
            "generation_model": getattr(self.generator, "last_model_used", "Apple Diagnostic Engine"),
            "evidence": retrieved_examples
        }

    def predict(self, customer_text: str) -> Dict[str, Any]:
        """Backwards-compatible interface for benchmark eval harness."""
        resp = self.respond(customer_text)
        action_str = "escalate" if resp["decision"] == "ESCALATE" else "auto_handle"
        
        # Raw formats for benchmark harness
        raw_items = [
            {
                "customer_query": e["customer_message"],
                "historical_reply": e["historical_response"],
                "similarity_score": e["similarity"]
            }
            for e in resp["evidence"]
        ]
        
        return {
            "predicted_intent": resp["intent"],
            "intent_confidence": resp["intent_confidence"],
            "all_intent_probabilities": {resp["intent"]: resp["intent_confidence"]},
            "retrieval_similarity": resp["evidence"][0]["similarity"] if resp["evidence"] else 0.0,
            "retrieved_historical_resolutions": raw_items,
            "policy_action": action_str,
            "policy_reason": resp["escalation_reason"] or "ROUTINE_AUTO_HANDLE",
            "policy_metadata": {},
            "draft_reply": resp["reply"],
            "generation_model": resp.get("generation_model", "Apple Diagnostic Engine"),
            "model_type": "embedding_dense_rag_agent"
        }
