"""
Historical Response Retrieval Module
Performs vector similarity search over historical customer resolutions.
Ensures privacy masking on all retrieved evidence.
"""

import os
from typing import List, Dict, Any, Optional
from agent.retriever import HistoricalResolutionRetriever
from src.data.cleaner import mask_pii

class HistoricalRetriever:
    def __init__(self, index_path: str = "models/retrieval_index.npz"):
        if not os.path.exists(index_path) and os.path.exists("agent/retrieval_index.npz"):
            index_path = "agent/retrieval_index.npz"
        self.underlying = HistoricalResolutionRetriever(index_path=index_path)

    def retrieve(self, query: str, top_k: int = 3, filter_intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves top-K similar historical cases:
        Returns:
        {
            "retrieved_examples": [
                {
                    "similarity": 0.91,
                    "customer_message": "...",
                    "historical_response": "..."
                }
            ]
        }
        """
        raw_results = self.underlying.retrieve(query, top_k=top_k)
        
        examples = []
        for r in raw_results:
            cust_text = mask_pii(r.get("customer_query", ""))
            reply_text = mask_pii(r.get("historical_reply", ""))
            score = round(float(r.get("similarity_score", 0.0)), 4)
            
            examples.append({
                "similarity": score,
                "customer_message": cust_text,
                "historical_response": reply_text
            })
            
        return {"retrieved_examples": examples}
