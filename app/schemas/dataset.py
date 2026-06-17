from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from core.db.base import WorkflowState


class UserShortRead(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TableCatalogRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DatasetRead(BaseModel):
    id: int
    name: str

    table_catalog_id: int
    owner_id: int

    workflow_state: WorkflowState
    rejection_comment: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    table_catalog: Optional[TableCatalogRead] = None
    owner: Optional[UserShortRead] = None
    tags: List[TagRead] = []

    class Config:
        from_attributes = True
