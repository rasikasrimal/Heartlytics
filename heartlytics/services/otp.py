"""Lightweight in-memory OTP service with cooldown enforcement."""
from __future__ import annotations

import hmac
import secrets
import time
from dataclasses import dataclass
from hashlib import sha256


@dataclass
class OTPRecord:
    hash: str
    expiry: float
    last_sent: float
    attempts: int = 0


class OTPService:
    def __init__(self, ttl: int = 300, cooldown: int = 60):
        self.ttl = ttl
        self.cooldown = cooldown
        self._store: dict[str, OTPRecord] = {}

    def _hash(self, code: str) -> str:
        return sha256(code.encode()).hexdigest()

    def issue(self, key: str) -> str:
        now = time.time()
        rec = self._store.get(key)
        if rec and now - rec.last_sent < self.cooldown:
            raise RuntimeError("cooldown active")
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self._store[key] = OTPRecord(hash=self._hash(code), expiry=now + self.ttl, last_sent=now)
        return code

    def verify(self, key: str, code: str) -> bool:
        rec = self._store.get(key)
        if not rec or time.time() > rec.expiry:
            return False
        rec.attempts += 1
        return hmac.compare_digest(rec.hash, self._hash(code))

    def can_resend(self, key: str) -> bool:
        rec = self._store.get(key)
        if not rec:
            return True
        return time.time() - rec.last_sent >= self.cooldown
