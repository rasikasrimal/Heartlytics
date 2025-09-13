"""
Keyring Factory and Provider Selection Module

Factory pattern for KMS providers with singleton instance.
Supports: dev, aws, gcp, azure providers.
Auto-generates dev keys if none provided.

services/crypto/envelope.py - Envelope encryption/decryption logic
services/crypto/aead.py - AES-GCM encryption primitives
services/crypto/__init__.py - Keyring factory and provider selection
services/crypto/keyring.py - Key management interface

"""

import os
import base64
from .keyring import (
    DevKeyring,
    AwsKmsKeyring,
    GcpKmsKeyring,
    AzureKeyVaultKeyring,
    load_dev_keyring,
)

# Global singleton keyring instance
_keyring = None


def get_keyring():
    """Get configured keyring instance (singleton pattern)."""
    global _keyring
    if _keyring is not None:
        return _keyring
        
    # Get provider configuration from environment
    provider = os.environ.get("KMS_PROVIDER", "dev").lower()
    kid = os.environ.get("KMS_KEY_ID", "dev-master")
    
    if provider == "dev":
        # Development keyring with local AES key management
        kr = load_dev_keyring(kid)
        if kr is None:
            # Auto-generate random master key for dev setups
            key_b64 = base64.b64encode(os.urandom(32)).decode()
            os.environ["DEV_KMS_MASTER_KEY"] = key_b64
            kr = load_dev_keyring(kid)
        _keyring = kr
    elif provider == "aws":
        # AWS Key Management Service integration (placeholder)
        _keyring = AwsKmsKeyring(kid)
    elif provider == "gcp":
        # Google Cloud Key Management Service integration (placeholder)
        _keyring = GcpKmsKeyring(kid)
    elif provider == "azure":
        # Azure Key Vault integration (placeholder)
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
