"""
Reply Quality Evaluation Module
Benchmarks response quality across 3 candidate systems on the Golden Set:
1. Baseline 1: Generic Template
2. Baseline 2: Nearest Neighbor (Verbatim Retrieval)
3. Final System: Retrieval-Grounded Agent
"""

import json
import numpy as np
from typing import List, Dict, Any
from evaluation.llm_judge import LLMJudge
from tabulate import tabulate

def evaluate_replies(golden_records: List[Dict[str, Any]], agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    judge = LLMJudge()
    
    systems = {
        "Generic Template": [],
        "Nearest Neighbor": [],
        "Final Agent (Ours)": []
    }
    
    for gold, pred in zip(golden_records, agent_results):
        q = gold["customer_text"]
        ref = gold.get("reference_reply", "")
        intent = gold["true_intent"]
        
        # 1. Generic Template
        gen_reply = "Thanks for reaching out. Please contact our support team for assistance."
        s_gen = judge.evaluate_reply(q, gen_reply, ref, intent, "auto_handle")
        systems["Generic Template"].append(s_gen)
        
        # 2. Nearest Neighbor
        nn_reply = gold.get("historical_brand_reply", "")
        s_nn = judge.evaluate_reply(q, nn_reply, ref, intent, "auto_handle")
        systems["Nearest Neighbor"].append(s_nn)
        
        # 3. Final Agent
        agent_reply = pred.get("draft_reply", "")
        s_agent = judge.evaluate_reply(q, agent_reply, ref, intent, pred.get("policy_action", "auto_handle"))
        systems["Final Agent (Ours)"].append(s_agent)

    summary_table = []
    headers = ["System", "Groundedness", "Helpfulness", "Relevance", "Hallucination", "Overall Quality"]
    results_dict = {}

    for sys_name, scores in systems.items():
        avg_ground = np.mean([s["groundedness"] for s in scores])
        avg_help = np.mean([s["helpfulness"] for s in scores])
        avg_rel = np.mean([s["relevance"] for s in scores])
        avg_halluc = np.mean([s["hallucination"] for s in scores])
        avg_overall = np.mean([s["overall"] for s in scores])
        
        results_dict[sys_name] = {
            "groundedness": round(float(avg_ground), 2),
            "helpfulness": round(float(avg_help), 2),
            "relevance": round(float(avg_rel), 2),
            "hallucination": round(float(avg_halluc), 2),
            "overall": round(float(avg_overall), 2)
        }
        
        summary_table.append([
            sys_name,
            f"{avg_ground:.2f}/5",
            f"{avg_help:.2f}/5",
            f"{avg_rel:.2f}/5",
            f"{avg_halluc:.2f}/5",
            f"{avg_overall:.2f}/5"
        ])

    print("\n" + "=" * 75)
    print("                    REPLY BASELINE COMPARISON")
    print("=" * 75)
    print(tabulate(summary_table, headers=headers, tablefmt="github"))
    print("=" * 75 + "\n")
    
    return results_dict
