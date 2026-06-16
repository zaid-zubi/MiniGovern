from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.services.crud import crud
from core.logging import logger


async def log_audit_action(
    db: AsyncSession,
    *,
    actor_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    dataset_id: int | None = None,
    details: dict | None = None,
    can_commit: bool = False
) -> AuditLog:
    """
    Create an audit log entry.
    """

    logger.info(
        f"AUDIT | action={action} | entity={entity_type} "
        f"(id={entity_id}) | actor_id={actor_id} | dataset_id={dataset_id}"
    )

    audit = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        dataset_id=dataset_id,
        details=details,
    )

    if can_commit:
        await crud.post(db, AuditLog, audit)
    else:
        db.add(audit)

    logger.info(
        f"AUDIT created in memory: action={action}, entity={entity_type}, id={entity_id}"
    )

    return audit