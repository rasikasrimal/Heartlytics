"""Utility helpers for masking sensitive identifiers."""
from __future__ import annotations


def mask_email(email: str, keep_prefix: int = 3, keep_suffix: int = 3) -> str:
    """Return an email with the local part and domain masked.

    Examples
    --------
    >>> mask_email("verify@example.com")
    'ver***ify@*****.com'
    """
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)

    if len(local) < keep_prefix + keep_suffix:
        pre = local[:1]
        suf = local[-1:] if len(local) > 1 else ""
    else:
        pre = local[:keep_prefix]
        suf = local[-keep_suffix:] if keep_suffix else ""

    masked_local = f"{pre}***{suf}" if suf else f"{pre}***"
    if "." in domain:
        tld = domain.split(".")[-1]
        masked_domain = "*****." + tld
    else:
        masked_domain = "*****"
    return f"{masked_local}@{masked_domain}"
