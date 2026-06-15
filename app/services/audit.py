from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.services.crud import crud


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
    db.add(audit)

    return audit