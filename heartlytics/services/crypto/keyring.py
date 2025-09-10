import base64
import os
from abc import ABC, abstractmethod
from typing import Optional

try:  # pragma: no cover - optional dependency
    from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap  # type: ignore
except Exception:  # pragma: no cover - fallback when cryptography is missing
    aes_key_wrap = aes_key_unwrap = None
    import hashlib


class Keyring(ABC):
    """Simple interface for wrapping and unwrapping data keys."""

    @abstractmethod
    def current_kid(self) -> str:
        """Return current key identifier."""

    @abstractmethod
    def wrap(self, data_key: bytes) -> bytes:
        """Wrap (encrypt) ``data_key`` and return the wrapped bytes."""

    @abstractmethod
    def unwrap(self, wrapped: bytes) -> bytes:
        """Unwrap ``wrapped`` and return the plaintext data key."""


class DevKeyring(Keyring):
    """Development keyring using an AES key from ``DEV_KMS_MASTER_KEY`` env."""

    def __init__(self, master_key: bytes, kid: str):
        if len(master_key) not in {16, 24, 32}:
            raise ValueError("master key must be 128/192/256-bit")
        self.master_key = master_key
        self._kid = kid

    def current_kid(self) -> str:  # pragma: no cover - trivial
        return self._kid

    def wrap(self, data_key: bytes) -> bytes:
        if aes_key_wrap is None:
            digest = hashlib.sha256(self.master_key).digest()
            return bytes([b ^ digest[i % len(digest)] for i, b in enumerate(data_key)])
        return aes_key_wrap(self.master_key, data_key)

    def unwrap(self, wrapped: bytes) -> bytes:
        if aes_key_unwrap is None:
            digest = hashlib.sha256(self.master_key).digest()
            return bytes([b ^ digest[i % len(digest)] for i, b in enumerate(wrapped)])
        return aes_key_unwrap(self.master_key, wrapped)


class AwsKmsKeyring(Keyring):
    """Placeholder for AWS KMS integration."""

    def __init__(self, key_id: str):
        self.key_id = key_id
        # TODO: implement using boto3

    def current_kid(self) -> str:  # pragma: no cover - unimplemented
        return self.key_id

    def wrap(self, data_key: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError

    def unwrap(self, wrapped: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError


class GcpKmsKeyring(Keyring):
    """Placeholder for Google Cloud KMS integration."""

    def __init__(self, key_id: str):
        self.key_id = key_id
        # TODO: implement using google-cloud-kms

    def current_kid(self) -> str:  # pragma: no cover - unimplemented
        return self.key_id

    def wrap(self, data_key: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError

    def unwrap(self, wrapped: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError


class AzureKeyVaultKeyring(Keyring):
    """Placeholder for Azure Key Vault integration."""

    def __init__(self, key_id: str):
        self.key_id = key_id
        # TODO: implement using azure-keyvault-keys

    def current_kid(self) -> str:  # pragma: no cover - unimplemented
        return self.key_id

    def wrap(self, data_key: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError

    def unwrap(self, wrapped: bytes) -> bytes:  # pragma: no cover - unimplemented
        raise NotImplementedError


_DEF_MASTER_ENV = "DEV_KMS_MASTER_KEY"


def load_dev_keyring(kid: str) -> Optional[DevKeyring]:
    """Return a :class:`DevKeyring` if ``DEV_KMS_MASTER_KEY`` is set."""

    key_b64 = os.environ.get(_DEF_MASTER_ENV)
    if not key_b64:
        return None
    master_key = base64.b64decode(key_b64)
    return DevKeyring(master_key, kid)
