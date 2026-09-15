"""
Thread Reconstruction Module
Pairs incoming customer inquiries with verified brand replies.
"""

import pandas as pd
from typing import List, Dict, Any

def reconstruct_threads(df_raw: pd.DataFrame, brand_handle: str = "AppleSupport") -> pd.DataFrame:
    """
    Pairs customer inbound tweets with subsequent brand replies.
    Expects columns: tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
    """
    if 'customer_text' in df_raw.columns and 'brand_reply_text' in df_raw.columns:
        # Already paired format
        return df_raw
    
    # Reconstruct from raw TWCS format if provided
    inbounds = df_raw[df_raw['inbound'] == True].copy()
    outbounds = df_raw[df_raw['author_id'] == brand_handle].copy()
    
    # Merge inbound with outbounds where in_response_to_tweet_id == inbound.tweet_id
    paired = pd.merge(
        inbounds,
        outbounds,
        left_on='tweet_id',
        right_on='in_response_to_tweet_id',
        suffixes=('_cust', '_brand')
    )
    
    result = pd.DataFrame({
        'thread_id': paired['tweet_id_cust'].astype(str) + "_" + paired['tweet_id_brand'].astype(str),
        'customer_tweet_id': paired['tweet_id_cust'],
        'brand_reply_id': paired['tweet_id_brand'],
        'customer_text': paired['text_cust'],
        'brand_reply_text': paired['text_brand'],
        'customer_created_at': paired['created_at_cust'],
        'reply_created_at': paired['created_at_brand']
    })
    
    return result
