"""
Evaluation Module: Escalation & Policy Decisions
Computes precision, recall, F1, false auto-handle rate (unsafe rate), and asymmetric risk cost.
"""

from typing import List, Dict, Any

def evaluate_escalation(
    y_true: List[str],
    y_pred: List[str],
    cost_false_auto_handle: float = 5.0,
    cost_false_escalate: float = 1.0
) -> Dict[str, Any]:
    """
    Evaluates binary escalation decision:
    Positive class = 'escalate' (or 'ESCALATE')
    Negative class = 'auto_handle' (or 'AUTO_HANDLE')
    """
    total = len(y_true)
    tp = 0  # True Escalate
    fp = 0  # False Escalate (False Alarm)
    tn = 0  # True Auto-handle
    fn = 0  # False Auto-handle (Unsafe / Catastrophic Risk)

    for yt_raw, yp_raw in zip(y_true, y_pred):
        yt = yt_raw.lower()
        yp = yp_raw.lower()
        if yt == "escalate" and yp == "escalate":
            tp += 1
        elif yt in ["auto_handle", "auto"] and yp == "escalate":
            fp += 1
        elif yt in ["auto_handle", "auto"] and yp in ["auto_handle", "auto"]:
            tn += 1
        elif yt == "escalate" and yp in ["auto_handle", "auto"]:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    total_escalate_ground_truth = tp + fn
    total_auto_ground_truth = tn + fp
    
    # False Auto-Handle Rate (Unsafe Auto Rate: FN / (TP + FN))
    unsafe_auto_handle_rate = fn / total_escalate_ground_truth if total_escalate_ground_truth > 0 else 0.0
    # False Escalation Rate (FP / (TN + FP))
    false_escalation_rate = fp / total_auto_ground_truth if total_auto_ground_truth > 0 else 0.0
    
    # Asymmetric Cost
    total_asym_cost = (fn * cost_false_auto_handle) + (fp * cost_false_escalate)
    cost_per_query = total_asym_cost / total if total > 0 else 0.0

    return {
        "escalation_precision": round(precision, 4),
        "escalation_recall": round(recall, 4),
        "escalation_f1": round(f1, 4),
        "unsafe_auto_handle_count": fn,
        "unsafe_auto_handle_rate": round(unsafe_auto_handle_rate, 4),
        "false_escalation_count": fp,
        "false_escalation_rate": round(false_escalation_rate, 4),
        "true_positives": tp,
        "true_negatives": tn,
        "total_evaluated": total,
        "asymmetric_cost_per_query": round(cost_per_query, 4),
        "asymmetric_penalty_total": round(total_asym_cost, 2)
    }
