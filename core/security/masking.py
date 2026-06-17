import re

from core.db.base import SensitivityLevel, UserRole

EMAIL_RE = re.compile(r"(^[^@]{1})[^@]*(@.*$)")


def should_mask(role: str, sensitivity: SensitivityLevel | None) -> bool:
    """
    Only admin can see raw PII.
    Viewer + Editor must see masked values for PII/SENSITIVE_PII.
    """
    if role == UserRole.ADMIN:
        return False

    return sensitivity in [
        SensitivityLevel.PII,
        SensitivityLevel.SENSITIVE_PII,
    ]


# -------------------------
# Masking strategies
# -------------------------


def mask_email(value: str) -> str:
    if not value or "@" not in value:
        return value
    return EMAIL_RE.sub(r"\1***\2", value)


def mask_phone(value: str) -> str:
    if not value:
        return value

    cleaned = re.sub(r"[^\d+]", "", value)

    if len(cleaned) <= 6:
        return "***"

    return cleaned[:4] + "***" + cleaned[-3:]


def mask_national_id(value: str) -> str:
    if not value:
        return value

    if len(value) <= 4:
        return "*" * len(value)

    return value[:2] + "***" + value[-2:]


def mask_generic(value: str) -> str:
    if not value:
        return value

    if len(value) <= 2:
        return "*" * len(value)

    return value[0] + "***" + value[-1]


# -------------------------
# Dispatcher
# -------------------------


def mask_value(value: str, column_name: str, sensitivity: SensitivityLevel | None) -> str:
    """
    Central masking router.
    Uses BOTH:
    - sensitivity level (primary)
    - column name (fallback)
    """

    if value is None:
        return value

    col = (column_name or "").lower()

    # PII-level routing
    if sensitivity == SensitivityLevel.PII:
        if "email" in col:
            return mask_email(value)
        if "phone" in col or "mobile" in col:
            return mask_phone(value)
        return mask_generic(value)

    # Sensitive PII (stronger masking)
    if sensitivity == SensitivityLevel.SENSITIVE_PII:
        if "national" in col or "nid" in col:
            return mask_national_id(value)
        return mask_generic(value)

    return value
