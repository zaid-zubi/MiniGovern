from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=3306, ge=1, le=65535)
    database: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=255)


class DataSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    host: str | None = Field(default=None, min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    database: str | None = Field(default=None, min_length=1, max_length=100)
    username: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=1, max_length=255)


class DataSourceRead(BaseModel):
    id: int
    name: str
    host: str
    port: int
    database: str
    username: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CategoryRead(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}
class ListDataSourceWithCategories(DataSourceRead):
    categories: list[CategoryRead]