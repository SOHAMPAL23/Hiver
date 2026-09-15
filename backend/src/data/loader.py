"""
Data Loader Module
Loads conversation pairs and retrieval datasets with optional subsampling.
"""

import os
import pandas as pd
from typing import Optional

def load_clean_data(file_path: str = "data/samples/apple_support_clean.parquet", max_rows: Optional[int] = None) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Clean dataset not found at {file_path}")
    df = pd.read_parquet(file_path)
    if max_rows and len(df) > max_rows:
        df = df.iloc[:max_rows].copy()
    return df

def load_retrieval_corpus(file_path: str = "data/samples/retrieval_corpus.parquet") -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Retrieval corpus not found at {file_path}")
    return pd.read_parquet(file_path)
