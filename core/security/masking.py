# app/core/security/masking.py

import re

from core.db.base import UserRole

EMAIL_RE = re.compile(r"(^[^@]{1})[^@]*(@.*$)")


def mask_email(value: str) -> str:
    if not value or "@" not in value:
        return value
    return EMAIL_RE.sub(r"\1***\2", value)


def mask_generic(value: str) -> str:
    if not value:
        return value
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "***" + value[-1]


def should_mask(role: str) -> bool:
    return role != UserRole.ADMIN
