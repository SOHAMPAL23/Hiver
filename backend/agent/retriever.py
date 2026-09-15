"""
Phase 4: Agent Component - Historical Resolution Retriever
Dense semantic search engine over historical (customer_query, apple_reply) pairs.
Uses all-MiniLM-L6-v2 embeddings and cosine similarity to retrieve top-k
grounded historical resolutions for any incoming customer issue.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

CORPUS_PATH = "data/samples/retrieval_corpus.parquet"
INDEX_PATH = "agent/retrieval_index.npz"

class HistoricalResolutionRetriever:
    def __init__(self, corpus_path: str = CORPUS_PATH, index_path: str = INDEX_PATH, max_index_size: int = 8000):
        self.corpus_path = corpus_path
        self.index_path = index_path
        self.max_index_size = max_index_size
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.records = []
        self.embeddings = None
        
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.build_index()

    def build_index(self):
        print(f"[*] Building dense retrieval index from {self.corpus_path}...")
        df = pd.read_parquet(self.corpus_path)
        
        # Select balanced high-quality resolved pairs
        sample_df = df.sample(n=min(self.max_index_size, len(df)), random_state=42).reset_index(drop=True)
        self.records = sample_df.to_dict('records')
        
        texts = [r['customer_text'] for r in self.records]
        print(f"[*] Encoding {len(texts)} historical customer queries...")
        self.embeddings = self.embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        # Store embeddings and textual metadata
        np.savez_compressed(
            self.index_path,
            embeddings=self.embeddings,
            customer_texts=np.array([r['customer_text'] for r in self.records], dtype=object),
            brand_replies=np.array([r['brand_reply_text'] for r in self.records], dtype=object),
            thread_ids=np.array([r['thread_id'] for r in self.records], dtype=object)
        )
        print(f"[OK] Saved dense retrieval index ({len(self.records)} pairs) to {self.index_path}")

    def load_index(self):
        print(f"[*] Loading dense retrieval index from {self.index_path}...")
        data = np.load(self.index_path, allow_pickle=True)
        self.embeddings = data['embeddings']
        c_texts = data['customer_texts']
        b_replies = data['brand_replies']
        t_ids = data['thread_ids']
        
        self.records = [
            {'thread_id': t_ids[i], 'customer_text': c_texts[i], 'brand_reply_text': b_replies[i]}
            for i in range(len(c_texts))
        ]
        print(f"[OK] Loaded {len(self.records)} indexed resolution pairs.")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vec = self.embedder.encode([query], normalize_embeddings=True)[0]
        # Cosine similarity via dot product of normalized vectors
        scores = np.dot(self.embeddings, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            rec = self.records[idx]
            results.append({
                "thread_id": rec['thread_id'],
                "customer_query": rec['customer_text'],
                "historical_reply": rec['brand_reply_text'],
                "similarity_score": float(scores[idx])
            })
        return results

if __name__ == "__main__":
    retriever = HistoricalResolutionRetriever(max_index_size=1500)
    test_q = "AirPods keep dropping connection with my MacBook"
    matches = retriever.retrieve(test_q, top_k=2)
    print(f"\nRetriever Test Output for: '{test_q}'")
    for i, m in enumerate(matches):
        print(f"\nMatch {i+1} (Cosine Sim: {m['similarity_score']:.3f}):")
        print(f"  Historical Query: {m['customer_query']}")
        print(f"  Brand Reply: {m['historical_reply']}")
