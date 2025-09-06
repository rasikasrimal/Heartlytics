import base64
import hmac
import os
import hashlib


def compute_blind_index(value: str, normalize: bool = True) -> bytes:
    if normalize:
        value = value.strip().lower()
    key_b64 = os.environ.get("DEV_KMS_IDX_KEY")
    if not key_b64:
        raise RuntimeError("DEV_KMS_IDX_KEY not set")
    key = base64.b64decode(key_b64)
    return hmac.new(key, value.encode(), hashlib.sha256).digest()
