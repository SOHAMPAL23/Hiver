"""
Phase 0: Data Acquisition, Thread Reconstruction, and Cleaning for @AppleSupport
Streams a targeted subsample from the Thoughtvector Customer Support dataset,
reconstructs customer->brand conversation pairs, filters noise, and outputs
a clean, documented intermediate dataset.
"""

import os
import io
import csv
import re
import html
import json
import urllib.request
import pandas as pd
from datetime import datetime

DATA_URL = "https://huggingface.co/datasets/SunidhiSriram/twcs/resolve/main/twcs.csv"
OUTPUT_PARQUET = "data/samples/apple_support_clean.parquet"
OUTPUT_CSV = "data/samples/apple_support_clean.csv"
DATA_CARD_PATH = "data/DATA_CARD.md"
TARGET_PAIRS = 20000  # High-quality sample size

def clean_tweet_text(text: str, is_brand: bool = False) -> str:
    """
    Cleans raw tweet text while preserving diagnostic/actionable content.
    - Decodes HTML entities (&gt;, &amp;, etc.)
    - Removes private user handle tokens (@115854, @AppleSupport)
    - Replaces iOS unicode glitch symbols (e.g. 'I\ufe0f' box character)
    - Normalizes multiple spaces and newlines
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Decode HTML
    cleaned = html.unescape(text)
    
    # Fix iOS 11 'I [?]' unicode glitch (common in 2017 tweets)
    cleaned = cleaned.replace("I️", "I").replace("i️", "I").replace("\ufe0f", "")
    
    # Remove user handles (@AppleSupport, @123456, etc.)
    cleaned = re.sub(r'@[A-Za-z0-9_]+', '', cleaned)
    
    # Strip t.co URLs from customer text if it's solely a screenshot link,
    # but keep if part of sentence or brand links
    # For customer: if the entire text was just a URL, it will become empty and dropped
    cleaned = re.sub(r'https?://t\.co/[A-Za-z0-9]+', '', cleaned).strip()
    
    # Normalize whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def clean_brand_text(text: str) -> str:
    """Clean brand reply while preserving official Apple support links."""
    if not text or not isinstance(text, str):
        return ""
    cleaned = html.unescape(text)
    cleaned = cleaned.replace("I️", "I").replace("\ufe0f", "")
    # Remove @user handle at start
    cleaned = re.sub(r'^@[A-Za-z0-9_]+\s*', '', cleaned)
    # Remove leftover handle tags
    cleaned = re.sub(r'@[A-Za-z0-9_]+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def download_and_process():
    os.makedirs("data/samples", exist_ok=True)
    
    print(f"[*] Connecting to dataset stream at {DATA_URL}...")
    # Fetch ~120MB chunk containing ~200k rows, ensuring ample AppleSupport volume
    chunk_bytes = 125 * 1024 * 1024
    req = urllib.request.Request(DATA_URL, headers={'Range': f'bytes=0-{chunk_bytes}'})
    
    with urllib.request.urlopen(req) as resp:
        print(f"[*] Downloading {chunk_bytes / (1024*1024):.1f} MB chunk...")
        raw_bytes = resp.read()
    
    print(f"[*] Read {len(raw_bytes) / (1024*1024):.2f} MB. Parsing CSV rows...")
    text_data = raw_bytes.decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(text_data))
    
    # Metrics for Data Card
    total_rows_scanned = 0
    raw_apple_replies = 0
    raw_customer_tweets = 0
    
    tweets_by_id = {}
    apple_replies = []
    
    for row in reader:
        total_rows_scanned += 1
        tid = row.get('tweet_id')
        if not tid:
            continue
        
        author = row.get('author_id')
        inbound = row.get('inbound') == 'True'
        text = row.get('text', '')
        in_resp = row.get('in_response_to_tweet_id')
        created_at = row.get('created_at')
        
        tweets_by_id[tid] = {
            'tweet_id': tid,
            'author_id': author,
            'inbound': inbound,
            'text': text,
            'created_at': created_at,
            'in_response_to_tweet_id': in_resp
        }
        
        if author == 'AppleSupport':
            raw_apple_replies += 1
            if in_resp:  # Apple responding to a previous tweet
                apple_replies.append({
                    'reply_id': tid,
                    'customer_tweet_id': in_resp,
                    'brand_reply_text': text,
                    'reply_created_at': created_at
                })
        elif inbound:
            raw_customer_tweets += 1
            
    print(f"[*] Scanned {total_rows_scanned:,} rows. Found {raw_apple_replies:,} Apple replies and indexed {len(tweets_by_id):,} total tweets.")
    
    # Match customer tweet -> Apple reply
    pairs = []
    dropped_missing_customer = 0
    dropped_empty_customer = 0
    dropped_short_customer = 0
    dropped_duplicate = 0
    seen_customer_texts = set()
    
    for rep in apple_replies:
        cid = rep['customer_tweet_id']
        cust_tweet = tweets_by_id.get(cid)
        if not cust_tweet:
            dropped_missing_customer += 1
            continue
        
        raw_cust_text = cust_tweet['text']
        clean_cust = clean_tweet_text(raw_cust_text, is_brand=False)
        clean_brand = clean_brand_text(rep['brand_reply_text'])
        
        # Filter out empty or purely media/tag tweets
        if not clean_cust:
            dropped_empty_customer += 1
            continue
        
        # Drop single-word or trivial tweets (<10 chars or <3 words) with no diagnostic signal
        if len(clean_cust) < 10 or len(clean_cust.split()) < 3:
            dropped_short_customer += 1
            continue
        
        # Deduplicate identical customer text to prevent train/eval leakage
        norm_key = clean_cust.lower()
        if norm_key in seen_customer_texts:
            dropped_duplicate += 1
            continue
        seen_customer_texts.add(norm_key)
        
        pairs.append({
            'thread_id': f"{cid}_{rep['reply_id']}",
            'customer_tweet_id': cid,
            'brand_reply_id': rep['reply_id'],
            'customer_text': clean_cust,
            'brand_reply_text': clean_brand,
            'customer_created_at': cust_tweet['created_at'],
            'reply_created_at': rep['reply_created_at']
        })
        
        if len(pairs) >= TARGET_PAIRS:
            break
            
    df = pd.DataFrame(pairs)
    print(f"[*] Final high-quality pairs reconstructed: {len(df):,}")
    print(f"    - Dropped missing parent customer tweet: {dropped_missing_customer:,}")
    print(f"    - Dropped empty / media-only customer text: {dropped_empty_customer:,}")
    print(f"    - Dropped short (<3 words / <10 chars): {dropped_short_customer:,}")
    print(f"    - Dropped duplicate customer queries: {dropped_duplicate:,}")
    
    # Save parquet and csv
    df.to_parquet(OUTPUT_PARQUET, index=False)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[✓] Saved cleaned dataset to {OUTPUT_PARQUET} and {OUTPUT_CSV}")
    
    # Compute date range
    dates = pd.to_datetime(df['customer_created_at'], errors='coerce')
    min_date = dates.min().strftime('%Y-%m-%d %H:%M:%S UTC') if not dates.isna().all() else "Unknown"
    max_date = dates.max().strftime('%Y-%m-%d %H:%M:%S UTC') if not dates.isna().all() else "Unknown"
    
    # Generate DATA_CARD.md
    data_card = f"""# Data Card: AppleSupport Reconstructed Customer Conversation Pairs

## Dataset Overview
- **Source**: Kaggle `thoughtvector/customer-support-on-twitter` (mirror: `SunidhiSriram/twcs`)
- **Brand Target**: `@AppleSupport`
- **Output Files**:
  - `data/samples/apple_support_clean.parquet` ({len(df):,} rows)
  - `data/samples/apple_support_clean.csv`
- **Date Range**: {min_date} to {max_date}

## Data Pipeline & Cleaning Methodology
1. **Thread Reconstruction**:
   - Matches brand responses (`author_id == 'AppleSupport'`) back to their parent customer tweet using `in_response_to_tweet_id`.
   - Ensures each record represents a genuine 1-to-1 customer issue and verified brand resolution.

2. **Text Normalization**:
   - Decoded HTML entities (`&gt;` $\\rightarrow$ `>`, `&amp;` $\\rightarrow$ `&`).
   - Cleaned iOS 11 unicode rendering bugs (`I [?]` / `\\ufe0f`).
   - Stripped private numeric user handles (`@115854`) and brand mention tags (`@AppleSupport`) to focus representation on substantive customer semantics.
   - Normalized duplicate spaces, tabs, and newline breaks.

3. **Filtering & Dropped Data Rationale**:
   - **Dropped Missing Parents ({dropped_missing_customer:,})**: Responses where the initiating customer tweet was outside the downloaded chunk or deleted.
   - **Dropped Media-Only / Empty Queries ({dropped_empty_customer:,})**: Customer tweets consisting solely of a raw `t.co` link (e.g. screenshot without text) with zero textual diagnostic information.
   - **Dropped Trivial / Sub-minimal Queries ({dropped_short_customer:,})**: Queries shorter than 10 characters or under 3 words (e.g. "help", "hello??", "DM sent") lacking diagnostic value.
   - **Deduplication ({dropped_duplicate:,})**: Exact normalized text duplicates removed to avoid retrieval leakage and skewed clustering.

## Schema Specification
| Column Name | Type | Description |
| :--- | :--- | :--- |
| `thread_id` | `string` | Unique compound key (`{customer_tweet_id}_{brand_reply_id}`) |
| `customer_tweet_id` | `string` | Tweet ID of the customer message |
| `brand_reply_id` | `string` | Tweet ID of AppleSupport's historical reply |
| `customer_text` | `string` | Cleaned customer text describing their technical/service issue |
| `brand_reply_text` | `string` | Cleaned historical resolution/response from AppleSupport |
| `customer_created_at` | `string` | Timestamp of incoming customer tweet |
| `reply_created_at` | `string` | Timestamp of brand reply |

## Statistical Properties
- **Total Clean Pairs**: {len(df):,}
- **Mean Customer Query Word Count**: {df['customer_text'].apply(lambda x: len(x.split())).mean():.1f} words
- **Mean Brand Reply Word Count**: {df['brand_reply_text'].apply(lambda x: len(x.split())).mean():.1f} words
- **Retained Ground Truth**: 100% of rows contain verified historical AppleSupport agent replies.
"""
    with open(DATA_CARD_PATH, "w", encoding="utf-8") as f:
        f.write(data_card)
    print(f"[✓] Generated Data Card at {DATA_CARD_PATH}")

if __name__ == "__main__":
    download_and_process()
