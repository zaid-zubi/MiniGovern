from numbers import Number
from typing import Any

from core.logging import logger


def profile_column(rows: list[dict], column_name: str) -> dict:
    logger.info(f"Profiling column: {column_name}, rows={len(rows)}")

    values = [row.get(column_name) for row in rows]
    non_null_values = [v for v in values if v is not None]

    total = len(values)

    null_count = calculate_null_count(values)
    distinct_count = calculate_distinct_count(values)
    null_percentage = calculate_null_percentage(total, null_count)
    valid_ratio = calculate_valid_ratio(total, null_count)

    result = {
        "row_count": total,
        "null_count": null_count,
        "null_percentage": null_percentage,
        "distinct_count": distinct_count,
        "valid_ratio": valid_ratio,
    }

    if not non_null_values:
        logger.info(f"Column profile completed: {column_name} (all values null)")
        return result

    sample_value = non_null_values[0]

    if isinstance(sample_value, Number):
        numeric_values = [v for v in non_null_values if isinstance(v, Number)]

        result.update(
            {
                "min": min(numeric_values),
                "max": max(numeric_values),
                "mean": round(sum(numeric_values) / len(numeric_values), 4),
            }
        )

    elif isinstance(sample_value, str):
        lengths = [len(v) for v in non_null_values if isinstance(v, str)]

        result.update(
            {
                "min_length": min(lengths),
                "max_length": max(lengths),
                "example_values": list(dict.fromkeys(non_null_values))[:5],
            }
        )

    logger.info(
        f"Column profile completed: {column_name} | "
        f"rows={total}, nulls={null_count}, distinct={distinct_count}"
    )

    return result


def calculate_null_percentage(total: int, null_count: int) -> float:
    if total == 0:
        return 0.0

    return round((null_count / total) * 100, 2)


def calculate_distinct_count(values: list[Any]) -> int:
    return len({v for v in values if v is not None})


def calculate_valid_ratio(total: int, null_count: int) -> float:
    if total == 0:
        return 0.0

    valid_count = total - null_count
    return round(valid_count / total, 4)


def calculate_null_count(values: list[Any]) -> int:
    return sum(1 for v in values if v is None)
