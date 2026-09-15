"""
Master Evaluation Benchmark Runner
Executes comprehensive evaluation of the AppleSupport Agent and baselines across:
- Intent Classification (Accuracy, Macro-F1, Confusion Matrix)
- Escalation & Policy Guardrails (Recall, False Auto-Handle Rate, Asymmetric Cost)
- Reply Generation (Groundedness, Helpfulness, Hallucination vs Baselines)
- Judge Calibration Audit (Human vs LLM Agreement)
Usage: python evaluation/evaluate_all.py
"""

import os
import sys
import json
import time
from tabulate import tabulate
from tqdm import tqdm

from src.agent import AppleSupportAgent
from baselines.trivial_baseline import TrivialBaseline
from baselines.simple_baseline import SimpleBaseline
from evaluation.evaluate_intent import evaluate_intent
from evaluation.evaluate_escalation import evaluate_escalation
from evaluation.evaluate_replies import evaluate_replies
from evaluation.human_vs_llm import run_human_vs_llm_agreement

GOLDEN_SET_PATH = "golden_eval/golden_eval.jsonl"
OUTPUT_JSON = "eval_results.json"

def run_all_evaluations():
    start_time = time.time()
    print("=" * 80)
    print("      APPLESUPPORT AI AGENT: COMPREHENSIVE BENCHMARK EVALUATION")
    print("=" * 80)

    # 1. Load Golden Set
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        golden_records = [json.loads(line) for line in f if line.strip()]
    print(f"[*] Loaded {len(golden_records)} golden evaluation records.")

    # 2. Initialize candidate systems
    print("\n[*] Initializing Systems...")
    trivial_sys = TrivialBaseline()
    simple_sys = SimpleBaseline()
    agent_sys = AppleSupportAgent()

    # 3. Evaluate Trivial Baseline
    print("\n---> Running Trivial Baseline...")
    triv_preds = [trivial_sys.predict(r["customer_text"]) for r in golden_records]

    # 4. Evaluate Simple Baseline
    print("\n---> Running Simple Baseline (TF-IDF)...")
    simp_preds = [simple_sys.predict(r["customer_text"]) for r in golden_records]

    # 5. Evaluate Final Agent
    print("\n---> Running AppleSupport Agent (Ours)...")
    agent_preds = [agent_sys.predict(r["customer_text"]) for r in tqdm(golden_records, desc="Scoring Agent")]

    # True labels
    y_true_intent = [r["true_intent"] for r in golden_records]
    y_true_action = [r["true_action"] for r in golden_records]

    # Metrics calculation
    systems_metrics = {}

    systems_data = [
        ("Trivial Baseline", triv_preds),
        ("Simple Baseline (TF-IDF)", simp_preds),
        ("AppleSupport Agent (Ours)", agent_preds)
    ]

    report_table = []
    headers = [
        "System", "Intent Macro-F1", "Intent Acc",
        "Escalation Recall", "Escalation Prec",
        "False Auto (Risk)", "Asym Cost/Q"
    ]

    for name, preds in systems_data:
        y_p_intent = [p["predicted_intent"] for p in preds]
        y_p_action = [p["policy_action"] for p in preds]

        intent_res = evaluate_intent(y_true_intent, y_p_intent)
        esc_res = evaluate_escalation(y_true_action, y_p_action)

        systems_metrics[name] = {
            "intent": intent_res,
            "escalation": esc_res
        }

        report_table.append([
            name,
            f"{intent_res['macro_f1'] * 100:.1f}%",
            f"{intent_res['accuracy'] * 100:.1f}%",
            f"{esc_res['escalation_recall'] * 100:.1f}%",
            f"{esc_res['escalation_precision'] * 100:.1f}%",
            esc_res['unsafe_auto_handle_count'],
            f"{esc_res['asymmetric_cost_per_query']:.2f}"
        ])

    print("\n" + "=" * 80)
    print("                          CORE EVALUATION RESULTS")
    print("=" * 80)
    print(tabulate(report_table, headers=headers, tablefmt="github"))
    print("=" * 80 + "\n")

    # 6. Evaluate Reply Quality
    reply_metrics = evaluate_replies(golden_records, agent_preds)
    systems_metrics["reply_benchmarks"] = reply_metrics

    # 7. Judge Calibration (Human vs LLM)
    agreement_res = run_human_vs_llm_agreement()
    systems_metrics["judge_human_calibration"] = agreement_res

    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(systems_metrics, f, indent=2)

    elapsed = time.time() - start_time
    print(f"\n[OK] Benchmark output saved to {OUTPUT_JSON}")
    print(f"[OK] Completed full evaluation in {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes).")

    return systems_metrics

if __name__ == "__main__":
    run_all_evaluations()
