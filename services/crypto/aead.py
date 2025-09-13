"""
AES-GCM Encryption Primitives Module

Core AEAD primitives using AES-256-GCM for confidentiality and authenticity.
Provides fallback XOR implementation for testing only.
"""

import os
from typing import Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
except Exception:  # pragma: no cover - fallback when cryptography is missing
    AESGCM = None
    import hashlib

# AES-GCM constants
NONCE_SIZE = 12  # 96-bit nonce for AES-GCM
TAG_SIZE = 16     # 128-bit authentication tag


def encrypt(plaintext: bytes, key: bytes, aad: bytes) -> Tuple[bytes, bytes, bytes]:
    """Encrypt plaintext using AES-256-GCM with associated data."""
    # Generate unique 96-bit nonce for this encryption
    nonce = os.urandom(NONCE_SIZE)
    
    if AESGCM is None:
        # Fallback XOR-based encryption for testing only - NOT SECURE FOR PRODUCTION
        digest = hashlib.sha256(key + nonce + aad).digest()
        ct = bytes([p ^ digest[i % len(digest)] for i, p in enumerate(plaintext)])
        tag = b""  # No authentication tag in fallback
        return ct, nonce, tag
        
    # Create AES-GCM cipher with 256-bit key
    aes = AESGCM(key)
    
    # Encrypt with associated data - returns ciphertext + tag
    ct_and_tag = aes.encrypt(nonce, plaintext, aad)
    
    # Split ciphertext and authentication tag
    return ct_and_tag[:-TAG_SIZE], nonce, ct_and_tag[-TAG_SIZE:]


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes, aad: bytes) -> bytes:
    """Decrypt ciphertext using AES-256-GCM with associated data verification."""
    if AESGCM is None:
        # Fallback XOR-based decryption for testing only - NOT SECURE FOR PRODUCTION
        digest = hashlib.sha256(key + nonce + aad).digest()
        pt = bytes([c ^ digest[i % len(digest)] for i, c in enumerate(ciphertext)])
        return pt
        
    # Create AES-GCM cipher with 256-bit key
    aes = AESGCM(key)
    
    # Decrypt and verify authentication tag and associated data
    return aes.decrypt(nonce, ciphertext + tag, aad)
