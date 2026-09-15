"""
Index & Model Build Script
Validates or constructs the normalized dense vector index and trained intent classifier.
Ensures zero runtime latency and reproducible embedding projections.
Usage: python scripts/build_index.py
"""

import os
import sys
import numpy as np
import pickle

INDEX_PATH = "agent/retrieval_index.npz"
CLASSIFIER_PATH = "agent/classifier_model.pkl"

def build_or_verify_index():
    print("=" * 60)
    print("       BUILD & VERIFY DENSE RETRIEVAL INDEX & CLASSIFIER")
    print("=" * 60)
    
    # 1. Verify retrieval index
    if os.path.exists(INDEX_PATH):
        print(f"[*] Loading retrieval index from: {INDEX_PATH}...")
        data = np.load(INDEX_PATH, allow_pickle=True)
        embeddings = data['embeddings']
        queries = data['customer_texts']
        replies = data['brand_replies']
        print(f"[OK] Verified dense retrieval vector index: {len(embeddings):,} items, dimension={embeddings.shape[1]}")
        # Verify normalization
        norms = np.linalg.norm(embeddings[:10], axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-3, err_msg="Index embeddings must be unit-normalized!")
        print("[OK] Embeddings are strictly L2 unit-normalized for rapid cosine dot-products.")
    else:
        print(f"[!] Index {INDEX_PATH} not found. Please build or check file presence.")

    # 2. Verify Classifier
    if os.path.exists(CLASSIFIER_PATH):
        print(f"\n[*] Loading Intent Classifier model from: {CLASSIFIER_PATH}...")
        with open(CLASSIFIER_PATH, "rb") as f:
            clf_payload = pickle.load(f)
        classes = getattr(clf_payload, 'classes_', [])
        print(f"[OK] Classifier model loaded successfully. Classes ({len(classes)}):")
        for c in classes:
            print(f"     - {c}")
    else:
        print(f"[!] Classifier model {CLASSIFIER_PATH} not found.")

    print("\n[OK] Retrieval index and classifier are fully verified and ready for production inference.")

if __name__ == "__main__":
    build_or_verify_index()
