from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan_job import ScanJob
from app.services.audit import log_audit_action
from app.services.crud import crud
from app.services.datasource import get_datasource
from core.db.base import JobStatus
from core.logging import logger
from core.settings.exceptions.scan_job import (
    DatasourceNotFound,
    ScanJobNotFound,
)


async def create_scan_job(
        datasource_id: int,
        db: AsyncSession,
        owner_id: int,
):
    logger.info(f"Creating scan job: datasource_id={datasource_id}, owner_id={owner_id}")

    datasource = await get_datasource(db, datasource_id)

    if not datasource:
        logger.warning(f"Datasource not found: id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    scan_job = ScanJob(
        datasource_id=datasource_id,
        status=JobStatus.PENDING,
        started_at=None,
        finished_at=None,
    )

    scan_job = await crud.post(db, ScanJob, scan_job)

    logger.info(
        f"Scan job created: id={scan_job.id}, datasource_id={datasource_id}, status=PENDING"
    )

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
        can_commit=True,
    )

    return scan_job


async def get_scan_job(scan_job_id: int, db: AsyncSession) -> ScanJob:
    logger.info(f"Fetching scan job: id={scan_job_id}")

    scan_job = await crud.get_one(db, ScanJob, id=scan_job_id)

    if not scan_job:
        logger.warning(f"Scan job not found: id={scan_job_id}")
        raise ScanJobNotFound(f"Scan job {scan_job_id} not found")

    logger.info(f"Scan job found: id={scan_job_id}, status={scan_job.status}")

    return scan_job


async def start_scan_job(scan_job: ScanJob, db: AsyncSession):
    logger.info(f"Starting scan job: id={scan_job.id}")

    scan_job.status = JobStatus.RUNNING
    scan_job.started_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(f"Scan job started: id={scan_job.id}, started_at={scan_job.started_at.isoformat()}")


async def complete_scan_job(
        scan_job: ScanJob,
        summary: dict,
        db: AsyncSession,
        actor_id: int,
) -> ScanJob:
    logger.info(f"Completing scan job: id={scan_job.id}")

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

    logger.info(
        f"Scan job completed: id={scan_job.id}, duration={scan_job.started_at} → {scan_job.finished_at}"
    )

    return scan_job


async def fail_scan_job(
        scan_job: ScanJob,
        error: Exception,
        db: AsyncSession,
        actor_id: int,
) -> ScanJob:
    logger.error(f"Failing scan job: id={scan_job.id}, error={str(error)}")

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

    logger.info(f"Scan job marked as FAILED: id={scan_job.id}")

    return scan_job


async def get_scan_job_status(db: AsyncSession, scan_job_id: int):
    job = await crud.get_one(db, ScanJob, id=scan_job_id)

    if not job:
        raise ScanJobNotFound()

    return {"scan_job_id": job.id, "status": job.status, "message": _get_status_message(job.status)}


def _get_status_message(status_value: JobStatus) -> str | None:
    if status_value == JobStatus.PENDING:
        return "Scan job is waiting to start"
    elif status_value == JobStatus.RUNNING:
        return "Scan job is currently running"
    elif status_value == JobStatus.COMPLETED:
        return "Scan completed successfully"
    elif status_value == JobStatus.FAILED:
        return "Scan failed"
    return None
