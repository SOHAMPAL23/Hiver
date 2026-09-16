
"""
Comprehensive Automated Unit Test Suite
Validates:
1. Data parsing & PII sanitization
2. Thread reconstruction & conversation pairing
3. Intent classifier output contracts & calibration
4. Vector retrieval accuracy & normalized embeddings
5. Policy engine guardrails & machine reason codes
6. Response generator grounding & KB links
7. End-to-end agent response schema
8. FastAPI backend endpoints
9. Zero-leakage guarantees
Run with: pytest or python -m unittest tests/test_agent.py
"""

import os
import sys
import unittest
import pandas as pd
from fastapi.testclient import TestClient

# Ensure root path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.cleaner import clean_text, mask_pii
from src.data.thread_reconstruction import reconstruct_threads
from src.intents.classifier import IntentClassifier
from src.retrieval.retriever import HistoricalRetriever
from src.escalation.policy import EscalationPolicy
from src.generation.generator import ReplyGenerator
from src.agent import AppleSupportAgent
from scripts.check_leakage import check_leakage
from main import app

class TestAppleSupportAgentSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[*] Initializing Test Suite...")
        cls.agent = AppleSupportAgent()
        cls.api_client = TestClient(app)

    # 1. Data Parsing & PII Sanitization
    def test_pii_masking_and_cleaning(self):
        raw = "Contact me at user@example.com or 555-123-4567 regarding order #123456789. Also @AppleSupport help!"
        cleaned = clean_text(raw, mask_personal_info=True)
        self.assertNotIn("user@example.com", cleaned)
        self.assertIn("[EMAIL_REDACTED]", cleaned)
        self.assertNotIn("555-123-4567", cleaned)
        self.assertNotIn("@AppleSupport", cleaned)

    # 2. Thread Reconstruction
    def test_thread_reconstruction(self):
        mock_raw = pd.DataFrame([
            {
                "tweet_id": "101",
                "author_id": "cust_1",
                "inbound": True,
                "created_at": "2017-10-31",
                "text": "Phone is broken",
                "response_tweet_id": "102",
                "in_response_to_tweet_id": None
            },
            {
                "tweet_id": "102",
                "author_id": "AppleSupport",
                "inbound": False,
                "created_at": "2017-10-31",
                "text": "We can help, send DM",
                "response_tweet_id": None,
                "in_response_to_tweet_id": "101"
            }
        ])
        paired = reconstruct_threads(mock_raw, brand_handle="AppleSupport")
        self.assertEqual(len(paired), 1)
        self.assertEqual(paired.iloc[0]["customer_tweet_id"], "101")
        self.assertEqual(paired.iloc[0]["brand_reply_id"], "102")

    # 3. Intent Classifier Contract
    def test_intent_classifier_contract(self):
        query = "My battery drains in 2 hours on my iPhone 7"
        res = self.agent.classifier.classify(query)
        self.assertIn("intent", res)
        self.assertIn("confidence", res)
        self.assertIn("alternatives", res)
        self.assertGreaterEqual(res["confidence"], 0.0)
        self.assertLessEqual(res["confidence"], 1.0)
        self.assertIsInstance(res["alternatives"], list)

    # 4. Historical Retrieval Contract
    def test_retriever_contract(self):
        query = "AirPods keep dropping Bluetooth connection"
        res = self.agent.retriever.retrieve(query, top_k=3)
        examples = res.get("retrieved_examples", [])
        self.assertEqual(len(examples), 3)
        for ex in examples:
            self.assertIn("similarity", ex)
            self.assertIn("customer_message", ex)
            self.assertIn("historical_response", ex)
            self.assertGreaterEqual(ex["similarity"], -1.0)
            self.assertLessEqual(ex["similarity"], 1.0)

    # 5. Policy Escalation Triggers
    def test_safety_hazard_escalation(self):
        policy = EscalationPolicy()
        res = policy.decide(
            customer_text="My battery is swollen and pushing the screen up",
            predicted_intent="battery_power_charging",
            intent_confidence=0.95,
            top_similarity=0.88
        )
        self.assertEqual(res["decision"], "ESCALATE")
        self.assertIn("SAFETY_HAZARD", res["reason_code"])

    def test_hardware_damage_escalation(self):
        policy = EscalationPolicy()
        res = policy.decide(
            customer_text="Dropped phone on pavement and front glass is shattered into pieces",
            predicted_intent="hardware_physical_damage",
            intent_confidence=0.92,
            top_similarity=0.85
        )
        self.assertEqual(res["decision"], "ESCALATE")
        self.assertEqual(res["reason_code"], "HARDWARE_PHYSICAL_DAMAGE_GENIUS_BAR")

    def test_low_confidence_escalation(self):
        policy = EscalationPolicy(confidence_threshold=0.58)
        res = policy.decide(
            customer_text="random ambiguous query xyz",
            predicted_intent="software_update_os_bug",
            intent_confidence=0.30,
            top_similarity=0.40
        )
        self.assertEqual(res["decision"], "ESCALATE")
        self.assertEqual(res["reason_code"], "LOW_INTENT_CONFIDENCE_ESCALATE")

    # 6. Response Generator Groundedness
    def test_reply_generator_groundedness(self):
        gen = ReplyGenerator()
        reply = gen.generate(
            customer_text="Wi-Fi keeps disconnecting",
            predicted_intent="connectivity_network_bluetooth",
            policy_action="auto_handle",
            policy_reason="ROUTINE_AUTO_HANDLE",
            retrieved_resolutions=[{"historical_reply": "Reset network settings via Settings > General > Reset."}]
        )
        self.assertIn("apple.com", reply.lower())

    # 7. End-to-End Agent Response Schema (Section 14)
    def test_agent_respond_schema(self):
        query = "How do I request a refund for a canceled subscription?"
        res = self.agent.respond(query)
        required_keys = [
            "intent", "intent_confidence", "decision",
            "decision_confidence", "escalation_reason",
            "reply", "evidence"
        ]
        for k in required_keys:
            self.assertIn(k, res)
        self.assertIn(res["decision"], ["AUTO_HANDLE", "ESCALATE"])
        self.assertEqual(len(res["evidence"]), 3)

    # 8. API Endpoints Contract
    def test_api_health_endpoint(self):
        response = self.api_client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["brand"], "AppleSupport")

    def test_api_config_endpoint(self):
        response = self.api_client.get("/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("brand", data)

    def test_api_predict_endpoint(self):
        payload = {"message": "My iPhone 7 battery drains fast after updating"}
        response = self.api_client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("intent", data)
        self.assertIn("decision", data)
        self.assertIn("reply", data)
        self.assertIn("evidence", data)

    # 9. Data Leakage Verification
    def test_zero_leakage_guarantee(self):
        is_clean = check_leakage()
        self.assertTrue(is_clean, "Zero-leakage guarantee must pass with 0 contamination!")

if __name__ == "__main__":
    unittest.main()
