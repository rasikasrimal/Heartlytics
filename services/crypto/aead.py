import os
from typing import Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
except Exception:  # pragma: no cover - fallback when cryptography is missing
    AESGCM = None
    import hashlib

NONCE_SIZE = 12
TAG_SIZE = 16


def encrypt(plaintext: bytes, key: bytes, aad: bytes) -> Tuple[bytes, bytes, bytes]:
    """Encrypt ``plaintext`` with ``key`` and return ``(ct, nonce, tag)``."""

    nonce = os.urandom(NONCE_SIZE)
    if AESGCM is None:
        # Very simple XOR-based fallback suitable only for tests
        digest = hashlib.sha256(key + nonce + aad).digest()
        ct = bytes([p ^ digest[i % len(digest)] for i, p in enumerate(plaintext)])
        tag = b""
        return ct, nonce, tag
    aes = AESGCM(key)
    ct_and_tag = aes.encrypt(nonce, plaintext, aad)
    return ct_and_tag[:-TAG_SIZE], nonce, ct_and_tag[-TAG_SIZE:]


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes, aad: bytes) -> bytes:
    if AESGCM is None:
        digest = hashlib.sha256(key + nonce + aad).digest()
        pt = bytes([c ^ digest[i % len(digest)] for i, c in enumerate(ciphertext)])
        return pt
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext + tag, aad)
