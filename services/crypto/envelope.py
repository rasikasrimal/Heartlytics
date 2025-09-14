"""
Envelope Encryption/Decryption Logic Module

Envelope encryption: data encrypted with unique DEK, DEK encrypted with master key.
Benefits: unique keys per item, master keys never leave KMS, cryptographic erasure, key rotation.
Context binding prevents copy-paste attacks.
"""


import os
from typing import Dict, Any

from .aead import encrypt, decrypt
from . import get_keyring

# Current key version for rotation support
KVER = 1


def encrypt_field(value: bytes, context: str) -> Dict[str, Any]:
    """Encrypt data using envelope encryption pattern."""
    # Convert string to bytes if needed
    if isinstance(value, str):
        value = value.encode()
        
    # Generate unique 256-bit data encryption key for this operation
    dk = os.urandom(32)
    
    # Get current keyring (KMS provider)
    keyring = get_keyring()
    kid = keyring.current_kid()
    
    # Encrypt data with AES-256-GCM using the DEK
    # Context is included as additional authenticated data (AAD)
    ct, nonce, tag = encrypt(value, dk, context.encode())
    
    # Wrap the DEK with the master key from KMS
    wrapped = keyring.wrap(dk)
    
    # Return complete envelope structure
    return {
        "ciphertext": ct,        # Encrypted data
        "nonce": nonce,          # 12-byte random nonce
        "tag": tag,              # 16-byte authentication tag
        "wrapped_dk": wrapped,   # DEK encrypted with master key
        "kid": kid,              # Key identifier
        "kver": KVER,            # Key version for rotation
    }


def decrypt_field(blob: Dict[str, Any], context: str) -> bytes:
    """Decrypt data from envelope encryption structure."""
    # Get keyring for unwrapping the DEK
    keyring = get_keyring()
    
    # Unwrap the DEK using the master key from KMS
    dk = keyring.unwrap(blob["wrapped_dk"])
    
    # Decrypt using AES-256-GCM with context verification
    return decrypt(
        blob["ciphertext"], 
        blob["nonce"], 
        blob["tag"], 
        dk, 
        context.encode()
    )
