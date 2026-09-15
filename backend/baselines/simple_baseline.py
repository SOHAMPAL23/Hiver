"""
Phase 3: Simple Baseline
1. Intent Classifier: TF-IDF Vectorizer + Cosine Similarity / 1-NN over indexed training corpus.
2. Reply Drafting: Verbatim most similar historical brand reply (pure verbatim retrieval, no synthesis).
3. Policy Engine: Keyword-based risk term matching (e.g. 'swollen', 'hacked', 'shattered') -> escalate; else auto-handle.
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any, List

DEFAULT_CORPUS = "data/samples/retrieval_corpus.parquet"

RISK_KEYWORDS = [
    "swollen", "swelled", "bulging", "smoke", "spark", "fire", "explosion",
    "shattered", "cracked screen", "water damage", "dropped in water", "broken glass",
    "hacked", "stolen", "unauthorized charge", "fraud", "scam", "compromised",
    "lawyer", "sue", "legal action"
]

class SimpleBaseline:
    def __init__(self, corpus_path: str = DEFAULT_CORPUS, max_train_samples: int = 5000):
        print(f"[*] Initializing SimpleBaseline with corpus from {corpus_path}...")
        if os.path.exists(corpus_path):
            df = pd.read_parquet(corpus_path)
        else:
            df = pd.read_parquet("data/samples/apple_support_clean.parquet")
            
        # Sample for fast, lightweight baseline fit
        sample_df = df.sample(n=min(max_train_samples, len(df)), random_state=42).reset_index(drop=True)
        self.customer_texts = sample_df['customer_text'].tolist()
        self.brand_replies = sample_df['brand_reply_text'].tolist()
        
        print(f"[*] Fitting TF-IDF Vectorizer on {len(self.customer_texts)} historical queries...")
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.customer_texts)
        
        # Keyword mappings for pseudo-intent labeling
        self.intent_keywords = {
            "battery_power_charging": ["battery", "drain", "charge", "charging", "hot", "cable", "charger", "overheating"],
            "software_update_os_bug": ["update", "ios 11", "ios", "restart", "loop", "boot", "logo", "crashing"],
            "connectivity_network_bluetooth": ["wifi", "wi-fi", "bluetooth", "airpods", "carrier", "cellular", "service"],
            "account_apple_id_icloud": ["apple id", "icloud", "password", "verification", "2fa", "iforgot", "locked"],
            "billing_subscriptions_appstore": ["refund", "subscription", "charged", "billing", "app store", "receipt"],
            "device_performance_storage": ["storage", "sluggish", "lag", "space", "freeze", "slow", "unresponsive"],
            "hardware_physical_damage": ["screen", "shattered", "cracked", "repair", "genius bar", "swollen", "glass"],
            "general_feedback_complaint": ["store", "worst", "terrible", "service", "disappointed", "apple", "sucks"]
        }

    def _infer_intent(self, text: str, top_sim: float, top_idx: int) -> tuple:
        t_lower = text.lower()
        
        # Score intent keywords
        best_intent = "software_update_os_bug"
        max_score = 0
        for intent, kw_list in self.intent_keywords.items():
            score = sum(1 for kw in kw_list if kw in t_lower)
            if score > max_score:
                max_score = score
                best_intent = intent
                
        confidence = float(min(1.0, max(0.2, top_sim * 0.9 + (0.1 * max_score))))
        return best_intent, confidence

    def predict(self, customer_text: str) -> Dict[str, Any]:
        query_vec = self.vectorizer.transform([customer_text])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        top_idx = int(np.argmax(sims))
        top_sim = float(sims[top_idx])
        
        intent, confidence = self._infer_intent(customer_text, top_sim, top_idx)
        verbatim_reply = self.brand_replies[top_idx]
        
        # Policy rule: Keyword matching for risk
        t_lower = customer_text.lower()
        matched_risk = [kw for kw in RISK_KEYWORDS if kw in t_lower]
        
        if matched_risk:
            action = "escalate"
            reason = f"KEYWORD_RISK_TRIGGERED_{matched_risk[0].upper().replace(' ', '_')}"
        elif top_sim < 0.15:
            action = "escalate"
            reason = "LOW_SIMILARITY_UNFAMILIAR_QUERY"
        else:
            action = "auto_handle"
            reason = "TFIDF_ROUTINE_MATCH"
            
        return {
            "predicted_intent": intent,
            "intent_confidence": confidence,
            "draft_reply": verbatim_reply,
            "retrieval_similarity": top_sim,
            "retrieved_reference_id": top_idx,
            "policy_action": action,
            "policy_reason": reason,
            "model_type": "tfidf_verbatim_baseline"
        }

if __name__ == "__main__":
    baseline = SimpleBaseline(max_train_samples=2000)
    sample_q = "My battery is expanding and pushing the screen up!"
    res = baseline.predict(sample_q)
    print("\nSimple Baseline Sample Output for:", sample_q)
    print(res)
