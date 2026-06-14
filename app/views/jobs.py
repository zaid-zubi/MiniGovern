from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models import ScanJob
from app.models.user import User
from app.schemas.scan_job import CreateScanJob
from app.services.crud import crud
from app.workers.scan_worker import run_scan_job

from core.db.session import get_db
from core.rbac import Permission

from app.services.scan_job import create_scan_job as create_scan_job_service


router = APIRouter(prefix="/scan-jobs", tags=["Scan Jobs"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_scan_job(
    body: CreateScanJob,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.SCAN_TRIGGER))],
):
    job = await create_scan_job_service(
        datasource_id=body.datasource_id,
        db=db,
        owner_id=current_user.id,
    )
    background_tasks.add_task(
        run_scan_job,
        job.id,
    )

    return job

@router.get("/")
async def get_scan_job(scan_job_id: int, db: AsyncSession = Depends(get_db)):
    scan_job = await crud.get_one(db, ScanJob, id=scan_job_id)
    return jsonable_encoder(scan_job)