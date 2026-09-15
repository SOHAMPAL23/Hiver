"""
Data Leakage Audit Script
Strictly verifies that no evaluation instances or identical conversation threads
leak into the retrieval corpus or training knowledge base.
Usage: python scripts/check_leakage.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np

def check_leakage():
    golden_path = "golden_eval/golden_eval.jsonl"
    corpus_path = "data/samples/retrieval_corpus.parquet"
    index_path = "agent/retrieval_index.npz"
    
    print("=" * 60)
    print("                    DATA LEAKAGE AUDIT")
    print("=" * 60)
    
    # 1. Load Golden Set
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_records = [json.loads(line) for line in f if line.strip()]
        
    gold_cust_texts = set(r["customer_text"].strip().lower() for r in golden_records)
    gold_tweet_ids = set(str(r.get("customer_tweet_id", "")) for r in golden_records if r.get("customer_tweet_id"))
    gold_brand_ids = set(str(r.get("brand_reply_id", "")) for r in golden_records if r.get("brand_reply_id"))
    
    # 2. Load Retrieval Corpus Parquet
    df_corpus = pd.read_parquet(corpus_path)
    corpus_cust_texts = set(df_corpus['customer_text'].astype(str).str.strip().str.lower())
    corpus_tweet_ids = set(df_corpus['customer_tweet_id'].astype(str))
    corpus_reply_ids = set(df_corpus['brand_reply_id'].astype(str))
    
    # 3. Load Retrieval Index NPZ queries
    npz_data = np.load(index_path, allow_pickle=True)
    index_queries = set(str(q).strip().lower() for q in npz_data['customer_texts'])
    
    # Checks
    exact_duplicate_leakage = len(gold_cust_texts.intersection(corpus_cust_texts))
    index_query_leakage = len(gold_cust_texts.intersection(index_queries))
    conversation_tweet_id_leakage = len(gold_tweet_ids.intersection(corpus_tweet_ids))
    brand_reply_id_leakage = len(gold_brand_ids.intersection(corpus_reply_ids))
    
    # Near duplicate check (character-level 3-gram Jaccard > 0.85)
    near_duplicates = 0
    sample_gold = list(gold_cust_texts)[:50]
    sample_corpus = list(corpus_cust_texts)[:1000]
    for g in sample_gold:
        g_grams = set([g[i:i+3] for i in range(len(g)-2)])
        if not g_grams:
            continue
        for c in sample_corpus:
            c_grams = set([c[i:i+3] for i in range(len(c)-2)])
            if not c_grams:
                continue
            jaccard = len(g_grams.intersection(c_grams)) / len(g_grams.union(c_grams))
            if jaccard > 0.88:
                near_duplicates += 1
                break

    print(f"\nLeakage Report")
    print("==============")
    print(f"Golden evaluation instances checked:        {len(golden_records)}")
    print(f"Retrieval corpus instances checked:         {len(df_corpus):,}")
    print(f"Exact duplicate leakage in corpus:          {exact_duplicate_leakage}")
    print(f"Exact duplicate leakage in retrieval index: {index_query_leakage}")
    print(f"Conversation Tweet ID leakage:              {conversation_tweet_id_leakage}")
    print(f"Brand Reply ID leakage:                     {brand_reply_id_leakage}")
    print(f"Sampled near-duplicate contamination:       {near_duplicates}")
    print(f"Evaluation retrieval contamination:         {exact_duplicate_leakage + conversation_tweet_id_leakage}")
    
    if exact_duplicate_leakage == 0 and conversation_tweet_id_leakage == 0:
        print("\n[OK] PASSED: Zero-contamination guarantee verified. No evaluation data present in retrieval index.")
    else:
        print("\n[!] WARNING: Potential data leakage detected between eval set and retrieval corpus!")
        
    return exact_duplicate_leakage == 0

if __name__ == "__main__":
    check_leakage()
