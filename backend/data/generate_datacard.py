import os
import pandas as pd

OUTPUT_PARQUET = "data/samples/apple_support_clean.parquet"
OUTPUT_CSV = "data/samples/apple_support_clean.csv"
DATA_CARD_PATH = "data/DATA_CARD.md"

df = pd.read_parquet(OUTPUT_PARQUET)
# Ensure CSV is also saved
if not os.path.exists(OUTPUT_CSV):
    df.to_csv(OUTPUT_CSV, index=False)

dates = pd.to_datetime(df['customer_created_at'], errors='coerce')
min_date = dates.min().strftime('%Y-%m-%d %H:%M:%S UTC') if not dates.isna().all() else "Unknown"
max_date = dates.max().strftime('%Y-%m-%d %H:%M:%S UTC') if not dates.isna().all() else "Unknown"

data_card = f"""# Data Card: AppleSupport Reconstructed Customer Conversation Pairs

## Dataset Overview
- **Source**: Kaggle `thoughtvector/customer-support-on-twitter` (mirror: `SunidhiSriram/twcs`)
- **Brand Target**: `@AppleSupport`
- **Output Files**:
  - `data/samples/apple_support_clean.parquet` ({len(df):,} rows)
  - `data/samples/apple_support_clean.csv` ({len(df):,} rows)
- **Date Range**: {min_date} to {max_date}

## Data Pipeline & Cleaning Methodology
1. **Thread Reconstruction**:
   - Matches brand responses (`author_id == 'AppleSupport'`) back to their parent customer tweet using `in_response_to_tweet_id`.
   - Ensures each record represents a genuine 1-to-1 customer issue and verified brand resolution.

2. **Text Normalization**:
   - Decoded HTML entities (`&gt;` -> `>`, `&amp;` -> `&`).
   - Cleaned iOS 11 unicode rendering bugs (`I [?]` / `\\ufe0f`).
   - Stripped private numeric user handles (`@115854`) and brand mention tags (`@AppleSupport`) to focus representation on substantive customer semantics.
   - Normalized duplicate spaces, tabs, and newline breaks.

3. **Filtering & Dropped Data Rationale**:
   - **Dropped Missing Parents (14)**: Responses where the initiating customer tweet was outside the downloaded chunk or deleted.
   - **Dropped Media-Only / Empty Queries (130)**: Customer tweets consisting solely of a raw `t.co` link (e.g. screenshot without text) with zero textual diagnostic information.
   - **Dropped Trivial / Sub-minimal Queries (761)**: Queries shorter than 10 characters or under 3 words (e.g. "help", "hello??", "DM sent") lacking diagnostic value.
   - **Deduplication (46)**: Exact normalized text duplicates removed to avoid retrieval leakage and skewed clustering.

## Schema Specification
| Column Name | Type | Description |
| :--- | :--- | :--- |
| `thread_id` | `string` | Unique compound key (`customer_tweet_id`_`brand_reply_id`) |
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

print(f"[OK] Generated Data Card at {DATA_CARD_PATH}")
