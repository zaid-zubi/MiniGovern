import re
from typing import Any

import httpx

from core.config import settings
from core.logging import logger

COUNTRY_API = settings.country_api  # base URL, e.g. https://restcountries.com/v3.1/name


async def detect_country(values: list[Any]) -> dict:
    """
    Detect if a column contains country names using external API validation.
    """
    try:
        values = [str(v).strip() for v in values if v is not None]

        if not values:
            return {}

        sample = values[:20]
        valid = 0

        async with httpx.AsyncClient(timeout=3.0) as client:
            for value in sample:
                try:
                    url = f"{COUNTRY_API}/{value}"

                    response = await client.get(url)

                    if response.status_code == 200:
                        valid += 1

                except Exception:
                    # fail-safe: ignore single request failure
                    continue

        if not sample:
            return {}

        ratio = valid / len(sample)

        if ratio >= 0.8:
            return {
                "semantic_type": "country",
                "valid_ratio": round(ratio, 2),
                "enrichment_source": "country_api",
            }

        return {}

    except Exception as e:
        logger.exception(f"Country enrichment failed: {e}")
        return {}


ISO_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "JOD",
    "SAR",
    "AED",
    "JPY",
    "CAD",
}


async def detect_currency(values: list[Any]) -> dict:
    """
    Detect if a column contains ISO currency codes.
    """
    try:
        values = [str(v).strip().upper() for v in values if v is not None]

        if not values:
            return {}

        sample = values[:50]

        valid = sum(1 for value in sample if value in ISO_CURRENCIES)

        ratio = valid / len(sample)

        if ratio >= 0.8:
            return {
                "semantic_type": "currency",
                "valid_ratio": round(ratio, 2),
                "enrichment_source": "iso_list",
            }

        return {}

    except Exception as e:
        logger.exception(f"Currency enrichment failed: {e}")
        return {}


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


async def detect_email_type(values: list[Any]) -> dict:
    try:
        values = [str(v).strip() for v in values if v is not None]

        if not values:
            return {}

        valid = sum(1 for value in values[:50] if EMAIL_PATTERN.match(value))

        ratio = valid / len(values[:50])

        if ratio >= 0.8:
            return {
                "semantic_type": "email",
                "valid_ratio": round(ratio, 2),
            }

        return {}

    except Exception as e:
        logger.exception(f"Email enrichment failed: {e}")
        return {}


async def enrich_column(
    column_name: str,
    values: list[Any],
) -> dict:
    try:
        detectors = [
            detect_country,
            detect_currency,
            detect_email_type,
        ]

        for detector in detectors:
            result = await detector(values)

            if result:
                return {
                    "semantic_type": result.get("semantic_type", "unknown"),
                    "valid_ratio": result.get("valid_ratio", 0.0),
                    "enrichment_source": result.get(
                        "enrichment_source",
                        detector.__name__,
                    ),
                }

        return {
            "semantic_type": "unknown",
            "valid_ratio": 0.0,
            "enrichment_source": None,
        }

    except Exception as e:
        logger.exception(f"Column enrichment failed: {e}")

        return {
            "semantic_type": "unknown",
            "valid_ratio": 0.0,
            "enrichment_source": None,
        }
