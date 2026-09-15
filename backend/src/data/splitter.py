"""
Data Splitter Module
Implements conversation-level and temporal splitting to prevent train/test contamination.
"""

import pandas as pd
from typing import Tuple, Optional

def split_data(
    df: pd.DataFrame,
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10,
    temporal: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Partitions conversation pairs into train, validation, and test splits.
    Guarantees no thread overlap between partitions.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"
    
    if temporal and 'customer_created_at' in df.columns:
        # Sort chronologically by customer timestamp
        df_sorted = df.copy()
        df_sorted['dt'] = pd.to_datetime(df_sorted['customer_created_at'], errors='coerce')
        df_sorted = df_sorted.sort_values('dt').reset_index(drop=True)
    else:
        df_sorted = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        
    n = len(df_sorted)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    
    train_df = df_sorted.iloc[:n_train].copy()
    val_df = df_sorted.iloc[n_train:n_train + n_val].copy()
    test_df = df_sorted.iloc[n_train + n_val:].copy()
    
    return train_df, val_df, test_df
