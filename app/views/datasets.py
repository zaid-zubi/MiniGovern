from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models.user import User
from app.schemas.language import Language
from app.services.dataset import get_datasets, get_dataset
from core.db.session import get_db
from core.rbac import Permission
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/dataset", tags=["Datasets"])


@router.get("/")
async def list_datasets(db: Annotated[AsyncSession, Depends(get_db)],
                        _: Annotated[User, Depends(require_permission(Permission.DATASET_READ))],
                        language: Annotated[Language, Query()] = Language.EN,
                        skip: int = Query(default=0, ge=0),
                        limit: int = Query(default=100, ge=1, le=200)):
    data = await get_datasets(db, skip, limit)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.GENERAL.READ.get(language),
                         data=data)


@router.get("/{dataset_id}")
async def read_dataset(dataset_id: int,
                       db: Annotated[AsyncSession, Depends(get_db)],
                       _: Annotated[User, Depends(require_permission(Permission.DATASET_READ))],
                       language: Annotated[Language, Query()] = Language.EN
                       ):
    data = await get_dataset(db, dataset_id)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.GENERAL.READ.get(language),
                         data=data)