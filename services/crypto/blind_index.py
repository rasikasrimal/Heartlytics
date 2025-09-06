import base64
import hmac
import os
import hashlib


def compute_blind_index(value: str, normalize: bool = True) -> bytes:
    if normalize:
        value = value.strip().lower()
    key_b64 = os.environ.get("DEV_KMS_IDX_KEY")
    if not key_b64:
        key_b64 = base64.b64encode(os.urandom(32)).decode()
        os.environ["DEV_KMS_IDX_KEY"] = key_b64
    key = base64.b64decode(key_b64)
    return hmac.new(key, value.encode(), hashlib.sha256).digest()
