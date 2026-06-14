from core.db.base import SensitivityLevel

PII_RULES = {
    "email": SensitivityLevel.PII,
    "e-mail": SensitivityLevel.PII,
    "phone": SensitivityLevel.PII,
    "mobile": SensitivityLevel.PII,
    "msisdn": SensitivityLevel.PII,

    "ssn": SensitivityLevel.SENSITIVE_PII,
    "national_id": SensitivityLevel.SENSITIVE_PII,
    "nid": SensitivityLevel.SENSITIVE_PII,
    "card": SensitivityLevel.SENSITIVE_PII,
    "credit_card": SensitivityLevel.SENSITIVE_PII,
}

import re

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")
NID_REGEX = re.compile(r"^[0-9]{8,20}$")
CARD_REGEX = re.compile(r"^[0-9]{13,19}$")

def is_email(value: str) -> bool:
    return isinstance(value, str) and bool(EMAIL_REGEX.match(value.strip()))


def is_phone(value: str) -> bool:
    if not isinstance(value, str):
        return False

    value = value.strip().replace(" ", "").replace("-", "")
    return bool(PHONE_REGEX.match(value))


def is_national_id(value: str) -> bool:
    return isinstance(value, str) and bool(NID_REGEX.match(value.strip()))


def is_credit_card(value: str) -> bool:
    if not isinstance(value, str):
        return False

    value = value.replace(" ", "").replace("-", "")
    return bool(CARD_REGEX.match(value))


def classify_value(value) -> SensitivityLevel | None:
    if value is None:
        return None

    if is_email(value):
        return SensitivityLevel.PII

    if is_phone(value):
        return SensitivityLevel.PII

    if is_credit_card(value):
        return SensitivityLevel.SENSITIVE_PII

    if is_national_id(value):
        return SensitivityLevel.SENSITIVE_PII

    return None


def classify_column(
    column_name: str,
    sample_values: list,
) -> tuple[SensitivityLevel, str | None]:

    name = column_name.lower().strip()

    for keyword, level in PII_RULES.items():
        if keyword in name:
            return level, f"name_match={keyword}"

    for v in sample_values:
        level = classify_value(v)

        if level == SensitivityLevel.PII:
            return SensitivityLevel.PII, "value_match=pii"

        if level == SensitivityLevel.SENSITIVE_PII:
            return SensitivityLevel.SENSITIVE_PII, "value_match=sensitive_pii"

    return SensitivityLevel.NONE, None