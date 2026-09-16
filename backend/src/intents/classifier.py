"""
Intent Classification Module
Provides calibrated multi-class intent prediction with alternative rankings and confidence estimates.
Includes Model A (TF-IDF Baseline) and Model B (Sentence-Transformer Dense Embeddings).
"""

import os
import sys
from typing import Dict, Any, List, Tuple
from agent.classifier import IntentClassifier as AgentIntentClassifier

class IntentClassifier:
    def __init__(self, model_path: str = "models/classifier_model.pkl"):
        if not os.path.exists(model_path) and os.path.exists("agent/classifier_model.pkl"):
            model_path = "agent/classifier_model.pkl"
        self.underlying_classifier = AgentIntentClassifier(model_path=model_path)

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies query text and returns structured response:
        {
            "intent": "...",
            "confidence": 0.87,
            "alternatives": [
                {"intent": "...", "confidence": 0.09}
            ]
        }
        """
        pred_intent, conf, all_probs = self.underlying_classifier.predict(text)
        
        # Sort alternatives by confidence descending
        sorted_items = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        alternatives = [
            {"intent": k, "confidence": round(float(v), 4)}
            for k, v in sorted_items if k != pred_intent
        ]
        
        return {
            "intent": pred_intent,
            "confidence": round(float(conf), 4),
            "alternatives": alternatives[:3]
        }

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        return self.underlying_classifier.predict(text)
