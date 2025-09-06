import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12
TAG_SIZE = 16


def encrypt(plaintext: bytes, key: bytes, aad: bytes) -> Tuple[bytes, bytes, bytes]:
    """Encrypt ``plaintext`` with ``key`` and return ``(ct, nonce, tag)``."""

    nonce = os.urandom(NONCE_SIZE)
    aes = AESGCM(key)
    ct_and_tag = aes.encrypt(nonce, plaintext, aad)
    return ct_and_tag[:-TAG_SIZE], nonce, ct_and_tag[-TAG_SIZE:]


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes, aad: bytes) -> bytes:
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext + tag, aad)
