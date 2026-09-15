"""
Phase 4: Agent Component - Intent Classifier
Uses all-MiniLM-L6-v2 dense embeddings with a calibrated multi-class Logistic Regression
model to classify customer queries into the 8 empirical intents.
Outputs predicted intent, calibrated confidence score, and full class probability vector.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sentence_transformers import SentenceTransformer

MODEL_PATH = "agent/classifier_model.pkl"
DEFAULT_CORPUS = "data/samples/retrieval_corpus.parquet"

INTENT_LABELS = [
    "software_update_os_bug",
    "battery_power_charging",
    "account_apple_id_icloud",
    "hardware_physical_damage",
    "connectivity_network_bluetooth",
    "billing_subscriptions_appstore",
    "device_performance_storage",
    "general_feedback_complaint"
]

class IntentClassifier:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.classifier = None
        
        if os.path.exists(self.model_path):
            self.load()
        else:
            print(f"[*] Classifier model not found at {self.model_path}. Training now...")
            self.train()

    def train(self, corpus_path: str = DEFAULT_CORPUS, samples_per_class: int = 150):
        print(f"[*] Training IntentClassifier from {corpus_path}...")
        df = pd.read_parquet(corpus_path)
        
        # Mine representative samples for each intent from historical corpus using precise semantic seeds
        intent_seed_rules = {
            "battery_power_charging": r"\b(battery|drain|charging|overheating|hot|charge|percentage|dies fast)\b",
            "software_update_os_bug": r"\b(update|ios 11|ios|reboot|boot loop|apple logo|stuck on update)\b",
            "connectivity_network_bluetooth": r"\b(wifi|wi-fi|bluetooth|airpods|no service|cellular|carrier)\b",
            "account_apple_id_icloud": r"\b(apple id|icloud|iforgot|verification code|password|locked account|2fa)\b",
            "billing_subscriptions_appstore": r"\b(refund|subscription|charged|billing|app store|itunes purchase|receipt)\b",
            "device_performance_storage": r"\b(storage|full|system data|sluggish|lag|slow|unresponsive|freezing)\b",
            "hardware_physical_damage": r"\b(shattered|cracked|broken screen|glass|repair cost|water damage|swollen|bent)\b",
            "general_feedback_complaint": r"\b(worst|terrible|horrible|service|store|genius bar|rude|unacceptable|joke)\b"
        }
        
        train_texts = []
        train_labels = []
        
        for intent, pattern in intent_seed_rules.items():
            matches = df[df['customer_text'].str.contains(pattern, case=False, regex=True)]
            sample = matches.sample(n=min(samples_per_class, len(matches)), random_state=42)
            for t in sample['customer_text']:
                train_texts.append(t)
                train_labels.append(intent)
                
        print(f"[*] Encoding {len(train_texts)} training examples...")
        X = self.embedder.encode(train_texts, show_progress_bar=False)
        y = np.array(train_labels)
        
        print("[*] Fitting Calibrated Multi-Class Logistic Regression...")
        base_lr = LogisticRegression(C=1.5, max_iter=1000, class_weight='balanced', random_state=42)
        calibrated_model = CalibratedClassifierCV(estimator=base_lr, method='sigmoid', cv=3)
        calibrated_model.fit(X, y)
        
        self.classifier = calibrated_model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.classifier, f)
        print(f"[OK] Trained & saved IntentClassifier to {self.model_path}")

    def load(self):
        print(f"[*] Loading IntentClassifier model from {self.model_path}...")
        with open(self.model_path, 'rb') as f:
            self.classifier = pickle.load(f)

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        vec = self.embedder.encode([text], show_progress_bar=False)
        probs = self.classifier.predict_proba(vec)[0]
        classes = self.classifier.classes_
        
        top_idx = int(np.argmax(probs))
        top_intent = str(classes[top_idx])
        top_confidence = float(probs[top_idx])
        
        prob_dict = {str(cls): float(prob) for cls, prob in zip(classes, probs)}
        return top_intent, top_confidence, prob_dict

if __name__ == "__main__":
    clf = IntentClassifier()
    test_msg = "My battery drops from 100% to 15% in less than an hour on iOS 11"
    intent, conf, all_p = clf.predict(test_msg)
    print("\nClassifier Test Output:")
    print(f"Text: '{test_msg}'")
    print(f"Predicted Intent: {intent} (Confidence: {conf:.3f})")
    print(f"Top 3 Probabilities: {sorted(all_p.items(), key=lambda x: x[1], reverse=True)[:3]}")
