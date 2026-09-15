"""
Data Cleaner & PII Masking Module
Provides text normalization and anonymization for Twitter customer support messages.
"""

import re
import html

def mask_pii(text: str) -> str:
    """Masks emails, phone numbers, order/tracking IDs, and credit card numbers."""
    if not text:
        return ""
    # 1. Mask email addresses
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_REDACTED]', text)
    # 2. Mask order/tracking numbers with hash
    text = re.sub(r'#\d{5,15}', '[ORDER_REDACTED]', text)
    # 3. Mask phone numbers
    text = re.sub(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE_REDACTED]', text)
    # 4. Mask credit card sequences
    text = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CARD_REDACTED]', text)
    return text

def clean_text(text: str, mask_personal_info: bool = True) -> str:
    """Cleans tweet text, unescapes HTML, strips handles, and fixes unicode glitches."""
    if not text or not isinstance(text, str):
        return ""
    cleaned = html.unescape(text)
    # Fix iOS 11 unicode glyph rendering glitch
    cleaned = cleaned.replace("I️", "I").replace("i️", "I").replace("\ufe0f", "")
    # Mask PII first before stripping handles
    if mask_personal_info:
        cleaned = mask_pii(cleaned)
    # Remove @user handle tokens
    cleaned = re.sub(r'(?<!\S)@[A-Za-z0-9_]+', '', cleaned)
    # Normalize multiple whitespace characters
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
