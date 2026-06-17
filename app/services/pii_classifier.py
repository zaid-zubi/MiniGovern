import re

from core.db.base import SensitivityLevel
from core.logging import logger

PII_RULES = {
    "emails": SensitivityLevel.PII,
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
        logger.info("Value classified as PII (emails pattern match)")
        return SensitivityLevel.PII

    if is_phone(value):
        logger.info("Value classified as PII (phone pattern match)")
        return SensitivityLevel.PII

    if is_credit_card(value):
        logger.warning("Value classified as SENSITIVE_PII (credit card detected)")
        return SensitivityLevel.SENSITIVE_PII

    if is_national_id(value):
        logger.warning("Value classified as SENSITIVE_PII (national ID detected)")
        return SensitivityLevel.SENSITIVE_PII

    return None


def classify_column(
        column_name: str,
        sample_values: list,
) -> tuple[SensitivityLevel, str | None]:
    name = column_name.lower().strip()

    logger.info(f"Classifying column: {column_name}, samples={len(sample_values)}")

    for keyword, level in PII_RULES.items():
        if keyword in name:
            logger.info(
                f"Column classified by name match: {column_name} -> {level.value} (keyword={keyword})"
            )
            return level, f"name_match={keyword}"

    pii_hits = 0
    sensitive_hits = 0

    for v in sample_values:
        level = classify_value(v)

        if level == SensitivityLevel.PII:
            pii_hits += 1

        elif level == SensitivityLevel.SENSITIVE_PII:
            sensitive_hits += 1

        if level == SensitivityLevel.PII:
            logger.info(f"PII detected in column {column_name} (value_match)")
            return SensitivityLevel.PII, "value_match=pii"

        if level == SensitivityLevel.SENSITIVE_PII:
            logger.warning(f"SENSITIVE_PII detected in column {column_name}")
            return SensitivityLevel.SENSITIVE_PII, "value_match=sensitive_pii"

    logger.info(
        f"Column classification result: {column_name} | "
        f"PII_hits={pii_hits}, sensitive_hits={sensitive_hits}"
    )

    return SensitivityLevel.NONE, None
