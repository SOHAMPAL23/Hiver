"""
Phase 5: Evaluation Harness - Intent Classification Metrics
Computes Accuracy, Macro-F1, Macro-Precision, Macro-Recall, and per-class metrics
against the 200-sample Golden Evaluation Set.
"""

from typing import List, Dict, Any
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score

INTENT_CLASSES = [
    "software_update_os_bug",
    "battery_power_charging",
    "account_apple_id_icloud",
    "hardware_physical_damage",
    "connectivity_network_bluetooth",
    "billing_subscriptions_appstore",
    "device_performance_storage",
    "general_feedback_complaint"
]

def evaluate_intent_predictions(
    y_true: List[str],
    y_pred: List[str],
    labels: List[str] = INTENT_CLASSES
) -> Dict[str, Any]:
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=labels, average='macro', zero_division=0)
    macro_prec = precision_score(y_true, y_pred, labels=labels, average='macro', zero_division=0)
    macro_rec = recall_score(y_true, y_pred, labels=labels, average='macro', zero_division=0)
    
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    
    per_class = {}
    for label in labels:
        if label in report:
            per_class[label] = {
                "precision": round(report[label]["precision"], 4),
                "recall": round(report[label]["recall"], 4),
                "f1_score": round(report[label]["f1-score"], 4),
                "support": int(report[label]["support"])
            }
            
    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "per_class": per_class
    }
