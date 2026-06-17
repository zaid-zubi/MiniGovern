from typing import Any, Optional

from pydantic import BaseModel


def serialize_data(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump()

    if isinstance(data, list):
        return [item.model_dump() if isinstance(item, BaseModel) else item for item in data]

    if isinstance(data, dict):
        return {k: v.model_dump() if isinstance(v, BaseModel) else v for k, v in data.items()}

    return data


def http_response(status: int, message: str, data: Optional[Any] = None) -> dict:
    return {
        "status_code": status,
        "message": message,
        "data": serialize_data(data),
    }
