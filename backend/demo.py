"""
Interactive & Scripted Demonstration Script
Demonstrates actual end-to-end model inference on real customer support queries:
1. Routine troubleshooting (Auto-Handle)
2. High-risk safety hazard (Immediate Human Escalation)
3. Account security breach (Immediate Escalation)
4. Hardware physical damage (Genius Bar Escalation)
Usage: python demo.py
"""

import sys
import os
import json
from src.agent import AppleSupportAgent

DEMO_QUERIES = [
    {
        "type": "ROUTINE AUTO-HANDLE",
        "query": "My iPhone 7 battery is draining 50% in an hour after updating to iOS 11"
    },
    {
        "type": "PHYSICAL SAFETY HAZARD (ESCALATION)",
        "query": "My battery is swollen and pushing the screen up, device is extremely hot to touch"
    },
    {
        "type": "ACCOUNT SECURITY BREACH (ESCALATION)",
        "query": "I think someone accessed my Apple ID and changed my payment details without authorization"
    },
    {
        "type": "HARDWARE DAMAGE (ESCALATION)",
        "query": "Dropped my phone on concrete and the front glass is shattered into pieces"
    }
]

def run_demo():
    print("=" * 75)
    print("           APPLESUPPORT AI AGENT: LIVE END-TO-END DEMO")
    print("=" * 75)
    
    agent = AppleSupportAgent()
    print("\n[OK] Agent loaded successfully. Running live inference...\n")

    for i, item in enumerate(DEMO_QUERIES, 1):
        q = item["query"]
        q_type = item["type"]
        
        print("-" * 75)
        print(f"CASE {i}: [{q_type}]")
        print(f"Customer:\n\"{q}\"\n")
        
        # Real model inference
        res = agent.respond(q)
        
        print(f"Intent:\n{res['intent']}")
        print(f"\nConfidence:\n{res['intent_confidence']:.2f}")
        print(f"\nDecision:\n{res['decision']}")
        print(f"\nReason:\n{res['escalation_reason'] or 'High confidence + strong historical evidence.'}")
        
        print(f"\nHistorical Evidence (Top {len(res['evidence'])} Retrieved Cases):")
        for idx, ev in enumerate(res["evidence"], 1):
            print(f"  {idx}. [Similarity: {ev['similarity']:.2f}]")
            print(f"     Customer: \"{ev['customer_message']}\"")
            print(f"     Response: \"{ev['historical_response']}\"")
            
        print(f"\nDraft Reply:\n{res['reply']}")
        print("-" * 75 + "\n")

if __name__ == "__main__":
    run_demo()
