"""Minimal TOTP generator and verifier (RFC 6238)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import quote


def random_base32(length: int = 16) -> str:
    return base64.b32encode(os.urandom(length)).decode("utf-8").rstrip("=")


def _normalize(secret: str) -> bytes:
    padding = "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(secret + padding)


def generate_totp(secret: str, for_time: int | None = None, step: int = 30, digits: int = 6) -> str:
    if for_time is None:
        for_time = int(time.time())
    counter = struct.pack(">Q", for_time // step)
    hm = hmac.new(_normalize(secret), counter, hashlib.sha1).digest()
    offset = hm[-1] & 0x0F
    code = (struct.unpack(">I", hm[offset : offset + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)


def verify_totp(secret: str, code: str, window: int = 1, step: int = 30, digits: int = 6) -> bool:
    now = int(time.time())
    for w in range(-window, window + 1):
        if generate_totp(secret, now + w * step, step, digits) == code:
            return True
    return False


def provisioning_uri(secret: str, name: str, issuer: str) -> str:
    label = quote(f"{issuer}:{name}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}"
