from app.services.emails.email import send_email
from app.services.emails.email_templates import (
    dataset_submitted_template,
    dataset_approved_template,
    dataset_rejected_template,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.services.auth import get_admins, get_user_by_id
from core.logging import logger


async def notify_admins_dataset_submitted(
        db: AsyncSession,
        dataset: Dataset,
) -> None:
    admins = await get_admins(db)

    recipients = [a.email for a in admins if a.email]

    if not recipients:
        logger.warning("No admin emails found")
        return

    subject, body = dataset_submitted_template(dataset.name)

    send_email(
        recipients=recipients,
        subject=subject,
        body=body,
    )


async def notify_owner_dataset_approved(
        db: AsyncSession,
        dataset: Dataset,
) -> None:
    owner = await get_user_by_id(db, dataset.owner_id)

    if not owner or not owner.email:
        logger.warning("No owner emails found")
        return

    subject, body = dataset_approved_template(dataset.name)

    send_email(
        recipients=[owner.email],
        subject=subject,
        body=body,
    )


async def notify_owner_dataset_rejected(
        db: AsyncSession,
        dataset: Dataset,
        comment: str | None = None,
) -> None:
    owner = await get_user_by_id(db, dataset.owner_id)

    if not owner or not owner.email:
        logger.warning("No owner emails found")
        return

    subject, body = dataset_rejected_template(
        dataset.name,
        comment,
    )

    send_email(
        recipients=[owner.email],
        subject=subject,
        body=body,
    )
