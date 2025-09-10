import os
from typing import Dict, Any

from .aead import encrypt, decrypt
from . import get_keyring


KVER = 1


def encrypt_field(value: bytes, context: str) -> Dict[str, Any]:
    """Return envelope-encrypted representation of ``value``."""

    if isinstance(value, str):
        value = value.encode()
    dk = os.urandom(32)
    keyring = get_keyring()
    kid = keyring.current_kid()
    ct, nonce, tag = encrypt(value, dk, context.encode())
    wrapped = keyring.wrap(dk)
    return {
        "ciphertext": ct,
        "nonce": nonce,
        "tag": tag,
        "wrapped_dk": wrapped,
        "kid": kid,
        "kver": KVER,
    }


def decrypt_field(blob: Dict[str, Any], context: str) -> bytes:
    """Decrypt ``blob`` created by :func:`encrypt_field`."""

    keyring = get_keyring()
    dk = keyring.unwrap(blob["wrapped_dk"])
    return decrypt(blob["ciphertext"], blob["nonce"], blob["tag"], dk, context.encode())
