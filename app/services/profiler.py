from typing import Any


def profile_column(rows: list[dict], column_name: str) -> dict:
    values = [row.get(column_name) for row in rows]

    total = len(values)

    null_count = calculate_null_count(values)
    distinct_count = calculate_distinct_count(values)
    null_percentage = calculate_null_percentage(total, null_count)
    valid_ratio = calculate_valid_ratio(total, null_count)

    return {
        "row_count": total,
        "null_count": null_count,
        "null_percentage": null_percentage,
        "distinct_count": distinct_count,
        "valid_ratio": valid_ratio
    }


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
