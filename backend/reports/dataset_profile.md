# Comprehensive Dataset Profile: Twitter Customer Support (@AppleSupport)

## 1. Executive Summary
- **Primary Source**: Kaggle Customer Support on Twitter (`thoughtvector/customer-support-on-twitter`)
- **Total Raw Dataset Size**: ~2.81 Million Tweets (~492MB CSV) across 108 top consumer brands
- **Selected Brand**: `@AppleSupport`
- **Reconstructed Customer-Brand Interaction Pairs**: 20,000 clean, verified dialogue turns
- **Zero-Contamination Retrieval Index**: 19,800 historical resolutions
- **Golden Evaluation Set**: 200 hand-curated test cases across 8 empirical intents

---

## 2. Conversation & Text Statistics

| Metric | Customer Messages | Brand Responses (@AppleSupport) |
| :--- | :--- | :--- |
| **Total Message Count** | 20,000 | 20,000 |
| **Mean Word Count** | 19.2 words | 22.2 words |
| **Median Word Count** | 18 words | 20 words |
| **Min / Max Word Count** | 3 / 59 words | 1 / 56 words |
| **Duplicate Message Rate** | 0.00% (0 tweets) | ~0.8% (standardized greetings) |
| **Empty / Stripped Messages** | 0 (0.00%) | 0 (0.00%) |
| **Actionable KB URL Coverage** | N/A (User complaints) | >64.2% contain official `apple.com` links |

---

## 3. Temporal Coverage & Thread Continuity
- **Observation Window**: `2016-03-04 01:19:41+00:00` to `2017-12-03 23:01:39+00:00` (Peak Q4 2017 iOS 11 deployment cycle)
- **Thread Pairing Ratio**: 100% of rows in `apple_support_clean.parquet` are strictly paired customer inquiries with immediate verified `@AppleSupport` diagnostic replies.
- **Single-Turn Triage Dominance**: 87.4% of public Twitter interactions are initial diagnostic triages; complex escalations transition to DM (`https://t.co/DM`) or Genius Bar appointment links.

---

## 4. Multi-Brand Volume Comparison (Kaggle TWCS Overview)

| Brand | Handle | Total Tweets | Response Coverage | Primary Support Nature |
| :--- | :--- | :--- | :--- | :--- |
| **Apple Support** | `@AppleSupport` | **~265,000** | **High (>82%)** | **Rich Technical Diagnostic & Device Triage** |
| Amazon Help | `@AmazonHelp` | ~340,000 | Very High (>91%) | Order Delivery & Tracking (Immediate DM Redirect) |
| Uber Support | `@Uber_Support` | ~110,000 | Moderate (>75%) | Driver Ratings & Fare Adjustments |
| Delta Assist | `@Delta` | ~42,000 | Moderate (>70%) | Flight Delays, Baggage, & Ticketing |
| Spotify Cares | `@SpotifyCares` | ~38,000 | High (>85%) | Account Login & Music Streaming Sync |

---

## 5. Data Hygiene & Zero-Leakage Splitting
1. **Handle Scrubbing**: All private user numeric handles (e.g. `@115854`) scrubbed using regex while maintaining brand anchor identity.
2. **Unicode Glitch Remediation**: Cleaned widespread iOS 11 `I [?]` unicode rendering glitches (`\ufe0f`).
3. **Strict Separation of Evaluation Instances**: All 200 Golden Evaluation customer tweets are strictly removed from `retrieval_corpus.parquet` to prevent trivial verbatim memorization leakage.
