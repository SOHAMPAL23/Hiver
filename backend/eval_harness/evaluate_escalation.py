"""
Phase 5: Evaluation Harness - Policy & Escalation Metrics with Asymmetric Cost
Evaluates binary escalation decision (auto_handle vs. escalate).
Integrates an Asymmetric Cost Matrix reflecting Apple's operational risk:
- False Auto-Handle (Cost = 5.0): Sending a safety hazard or compromised account to bot.
- False Escalate (Cost = 1.0): Routing a routine software reset to human agent.
"""

from typing import List, Dict, Any

def evaluate_escalation_decisions(
    y_true: List[str],
    y_pred: List[str],
    cost_false_auto_handle: float = 5.0,
    cost_false_escalate: float = 1.0
) -> Dict[str, Any]:
    """
    Positive class = 'escalate'
    Negative class = 'auto_handle'
    """
    total = len(y_true)
    tp = 0  # True Escalate
    fp = 0  # False Escalate (Predicted Escalate, True Auto)
    tn = 0  # True Auto
    fn = 0  # False Auto-Handle (Predicted Auto, True Escalate)
    
    for yt, yp in zip(y_true, y_pred):
        if yt == "escalate" and yp == "escalate":
            tp += 1
        elif yt == "auto_handle" and yp == "escalate":
            fp += 1
        elif yt == "auto_handle" and yp == "auto_handle":
            tn += 1
        elif yt == "escalate" and yp == "auto_handle":
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0
    
    # Asymmetric Cost Calculation
    total_cost = (fn * cost_false_auto_handle) + (fp * cost_false_escalate)
    normalized_cost = total_cost / total if total > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "escalation_precision": round(precision, 4),
        "escalation_recall": round(recall, 4),
        "escalation_specificity": round(specificity, 4),
        "true_positives_escalate": tp,
        "false_positives_false_escalate": fp,
        "true_negatives_auto": tn,
        "false_negatives_false_auto_handle": fn,
        "asymmetric_penalty_total": round(total_cost, 2),
        "asymmetric_cost_per_query": round(normalized_cost, 4),
        "cost_weights": {
            "false_auto_handle": cost_false_auto_handle,
            "false_escalate": cost_false_escalate
        }
    }
