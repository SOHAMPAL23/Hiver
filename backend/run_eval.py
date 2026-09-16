"""
Master Evaluation Runner: End-to-End Comparative Benchmark
Runs Trivial Baseline, Simple Baseline, and AppleSupport Agent over the 200-item
Golden Evaluation Set.
Evaluates:
1. Intent Classification (Macro-F1, Accuracy, Precision, Recall)
2. Escalation & Policy Guardrails (Precision, Recall, Asymmetric Cost Matrix)
3. Reply Quality Rubric (Groundedness, Actionability, Tone, Conciseness)
Emits Markdown tables and saves detailed eval_results.json.
Execution target: < 15 minutes on local CPU.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
from tabulate import tabulate
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from baselines.trivial_baseline import TrivialBaseline
from baselines.simple_baseline import SimpleBaseline
from agent.pipeline import AppleSupportAgent
from eval_harness.evaluate_intents import evaluate_intent_predictions
from eval_harness.evaluate_escalation import evaluate_escalation_decisions
from eval_harness.llm_judge import LLMJudge

GOLDEN_EVAL_PATH = "golden_eval/golden_eval.jsonl"
OUTPUT_RESULTS_JSON = "eval_results.json"

def run_evaluation():
    start_time = time.time()
    print("="*80)
    print("      APPLESUPPORT AI AGENT: RIGOROUS EVALUATION HARNESS BENCHMARK")
    print("="*80)

    # 1. Load Golden Set
    print(f"[*] Loading Golden Evaluation Set from {GOLDEN_EVAL_PATH}...")
    with open(GOLDEN_EVAL_PATH, "r", encoding="utf-8") as f:
        eval_records = [json.loads(line) for line in f if line.strip()]
    print(f"[OK] Loaded {len(eval_records)} hand-curated evaluation instances.")

    # 2. Instantiate Systems
    print("\n[*] Initializing Candidate Systems...")
    trivial = TrivialBaseline()
    simple = SimpleBaseline(max_train_samples=3000)
    agent = AppleSupportAgent()
    judge = LLMJudge()

    systems = {
        "Trivial Baseline": trivial,
        "Simple Baseline (TF-IDF)": simple,
        "AppleSupport Agent (Ours)": agent
    }

    ground_truth_intents = [r["true_intent"] for r in eval_records]
    ground_truth_actions = [r["true_action"] for r in eval_records]

    all_results = {}
    model_predictions = {name: [] for name in systems}

    # 3. Execute Predictions & Scoring
    print("\n[*] Executing Benchmark Runs across 200 Golden Instances...")
    for sys_name, model in systems.items():
        print(f"\n---> Evaluating: {sys_name}")
        preds = []
        pred_intents = []
        pred_actions = []
        rubric_scores = []

        for item in tqdm(eval_records, desc=f"Scoring {sys_name}"):
            res = model.predict(item["customer_text"])
            
            # Judge quality of generated reply
            j_score = judge.evaluate_reply(
                customer_text=item["customer_text"],
                draft_reply=res["draft_reply"],
                reference_reply=item["reference_reply"],
                true_intent=item["true_intent"],
                policy_action=res["policy_action"]
            )

            record_pred = {
                "eval_id": item["eval_id"],
                "customer_text": item["customer_text"],
                "true_intent": item["true_intent"],
                "predicted_intent": res["predicted_intent"],
                "intent_confidence": res.get("intent_confidence", 0.0),
                "true_action": item["true_action"],
                "policy_action": res["policy_action"],
                "policy_reason": res.get("policy_reason", "N/A"),
                "draft_reply": res["draft_reply"],
                "historical_brand_reply": item["historical_brand_reply"],
                "reference_reply": item["reference_reply"],
                "rubric_scores": j_score,
                "edge_case_category": item.get("edge_case_category", "standard"),
                "difficulty": item.get("difficulty", "medium")
            }
            preds.append(record_pred)
            pred_intents.append(res["predicted_intent"])
            pred_actions.append(res["policy_action"])
            rubric_scores.append(j_score)

        model_predictions[sys_name] = preds

        # Compute Metrics
        intent_metrics = evaluate_intent_predictions(ground_truth_intents, pred_intents)
        escalation_metrics = evaluate_escalation_decisions(ground_truth_actions, pred_actions, cost_false_auto_handle=5.0, cost_false_escalate=1.0)
        
        mean_groundedness = float(np.mean([s["groundedness"] for s in rubric_scores]))
        mean_actionability = float(np.mean([s["actionability"] for s in rubric_scores]))
        mean_tone = float(np.mean([s["tone_alignment"] for s in rubric_scores]))
        mean_conciseness = float(np.mean([s["conciseness"] for s in rubric_scores]))
        mean_overall = float(np.mean([s["overall_score"] for s in rubric_scores]))

        all_results[sys_name] = {
            "intent_metrics": intent_metrics,
            "escalation_metrics": escalation_metrics,
            "reply_quality": {
                "mean_groundedness": round(mean_groundedness, 2),
                "mean_actionability": round(mean_actionability, 2),
                "mean_tone": round(mean_tone, 2),
                "mean_conciseness": round(mean_conciseness, 2),
                "mean_overall_rubric": round(mean_overall, 2)
            }
        }

    elapsed_time = time.time() - start_time

    # 4. Generate Comparative Tables
    print("\n" + "="*80)
    print("                          FINAL EVALUATION REPORT")
    print("="*80)

    summary_rows = []
    for name, res in all_results.items():
        im = res["intent_metrics"]
        em = res["escalation_metrics"]
        rq = res["reply_quality"]

        summary_rows.append([
            name,
            f"{im['macro_f1']*100:.1f}%",
            f"{im['accuracy']*100:.1f}%",
            f"{em['escalation_recall']*100:.1f}%",
            f"{em['escalation_precision']*100:.1f}%",
            f"{em['false_negatives_false_auto_handle']}",
            f"{em['asymmetric_cost_per_query']:.2f}",
            f"{rq['mean_groundedness']:.2f}/5",
            f"{rq['mean_actionability']:.2f}/5",
            f"{rq['mean_overall_rubric']:.2f}/5"
        ])

    headers = [
        "System", "Intent Macro-F1", "Intent Acc", "Escalation Recall",
        "Escalation Prec", "False Auto (Risk)", "Asym Cost/Q",
        "Groundedness", "Actionability", "Overall Quality"
    ]
    table_str = tabulate(summary_rows, headers=headers, tablefmt="github")
    print(table_str)

    # 5. Extract Concrete Real Failure Modes from Agent Predictions
    agent_failures = []
    for p in model_predictions["AppleSupport Agent (Ours)"]:
        is_intent_error = p["predicted_intent"] != p["true_intent"]
        is_action_error = p["policy_action"] != p["true_action"]
        is_high_risk = (p["true_action"] == "escalate" and p["policy_action"] == "auto_handle")
        
        if is_intent_error or is_action_error or is_high_risk:
            agent_failures.append({
                "eval_id": p["eval_id"],
                "customer_text": p["customer_text"],
                "true_intent": p["true_intent"],
                "predicted_intent": p["predicted_intent"],
                "true_action": p["true_action"],
                "policy_action": p["policy_action"],
                "policy_reason": p["policy_reason"],
                "draft_reply": p["draft_reply"],
                "historical_brand_reply": p["historical_brand_reply"],
                "edge_case_category": p["edge_case_category"],
                "failure_type": "false_auto_handle_risk" if is_high_risk else ("intent_mismatch" if is_intent_error else "false_escalate")
            })

    output_payload = {
        "benchmark_metadata": {
            "evaluation_date": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            "eval_samples_count": len(eval_records),
            "elapsed_seconds": round(elapsed_time, 2)
        },
        "summary_table_markdown": table_str,
        "comparative_metrics": all_results,
        "agent_failure_cases": agent_failures[:20]  # Store top failure cases for failure analysis
    }

    with open(OUTPUT_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
    print(f"\n[OK] Detailed evaluation payload written to {OUTPUT_RESULTS_JSON}")
    print(f"[OK] Total evaluation completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes).")
    return output_payload

if __name__ == "__main__":
    import numpy as np
    run_evaluation()
