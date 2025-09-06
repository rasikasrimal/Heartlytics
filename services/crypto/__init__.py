import os
from .keyring import (
    DevKeyring,
    AwsKmsKeyring,
    GcpKmsKeyring,
    AzureKeyVaultKeyring,
    load_dev_keyring,
)

_keyring = None


def get_keyring():
    global _keyring
    if _keyring is not None:
        return _keyring
    provider = os.environ.get("KMS_PROVIDER", "dev").lower()
    kid = os.environ.get("KMS_KEY_ID", "dev-master")
    if provider == "dev":
        kr = load_dev_keyring(kid)
        if kr is None:
            raise RuntimeError("DEV_KMS_MASTER_KEY not configured")
        _keyring = kr
    elif provider == "aws":
        _keyring = AwsKmsKeyring(kid)
    elif provider == "gcp":
        _keyring = GcpKmsKeyring(kid)
    elif provider == "azure":
        _keyring = AzureKeyVaultKeyring(kid)
    else:
        raise ValueError(f"unknown KMS provider {provider}")
    return _keyring


__all__ = [
    "get_keyring",
    "DevKeyring",
    "AwsKmsKeyring",
    "GcpKmsKeyring",
    "AzureKeyVaultKeyring",
]
