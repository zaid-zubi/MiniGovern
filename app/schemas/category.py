from typing import Optional

from pydantic import BaseModel, Field


class CategoryIn(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
