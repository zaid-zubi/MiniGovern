from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan_job import ScanJob
from app.services.audit import log_audit_action
from app.services.crud import crud
from app.services.datasource import get_datasource
from core.db.base import JobStatus


async def create_scan_job(
        datasource_id: int,
        db: AsyncSession,
        owner_id: int,
):
    datasource = await get_datasource(db, datasource_id)

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found",
        )

    scan_job = ScanJob(
        datasource_id=datasource_id,
        status=JobStatus.PENDING,
        started_at=None,
        finished_at=None,
    )

    scan_job = await crud.post(db, ScanJob, scan_job)
    await log_audit_action(
        db,
        actor_id=owner_id,
        action="create_scan_job",
        entity_type="scan_job",
        entity_id=scan_job.id,
        dataset_id=None,
        details={
            "datasource_id": datasource_id,
            "status": JobStatus.PENDING.value,
        },
        can_commit=True
    )
    return scan_job


async def get_scan_job(
        scan_job_id: int,
        db,
) -> ScanJob | None:
    return await crud.get_one(
        db,
        ScanJob,
        id=scan_job_id,
    )


async def start_scan_job(scan_job: ScanJob, db: AsyncSession):
    scan_job.status = JobStatus.RUNNING
    scan_job.started_at = datetime.now(timezone.utc)
    await db.commit()


async def complete_scan_job(
        scan_job: ScanJob,
        summary: dict,
        db: AsyncSession,
        actor_id: int,
) -> ScanJob:
    scan_job.status = JobStatus.COMPLETED
    scan_job.finished_at = datetime.now(timezone.utc)
    scan_job.summary = summary
    await log_audit_action(
        db,
        actor_id=actor_id,
        action="complete_scan_job",
        entity_type="scan_job",
        entity_id=scan_job.id,
        details={
            "finished_at": scan_job.finished_at.isoformat(),
            "summary": summary,
        },
    )
    await db.commit()
    await db.refresh(scan_job)

    return scan_job


async def fail_scan_job(
        scan_job: ScanJob,
        error: Exception,
        db: AsyncSession,
        actor_id: int,
) -> ScanJob:
    scan_job.status = JobStatus.FAILED
    scan_job.finished_at = datetime.now(timezone.utc)
    scan_job.error_message = str(error)
    await log_audit_action(
        db,
        actor_id=actor_id,
        action="fail_scan_job",
        entity_type="scan_job",
        entity_id=scan_job.id,
        details={
            "error": str(error),
            "finished_at": scan_job.finished_at.isoformat(),
        },
    )
    await db.commit()
    await db.refresh(scan_job)

    return scan_job
