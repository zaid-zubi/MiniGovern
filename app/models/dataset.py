from sqlalchemy import ForeignKey, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, TimestampMixin, WorkflowState


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    table_catalog_id: Mapped[int] = mapped_column(ForeignKey("table_catalogs.id"), unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    workflow_state: Mapped[WorkflowState] = mapped_column(
        Enum(WorkflowState), default=WorkflowState.DRAFT
    )
    rejection_comment: Mapped[str | None] = mapped_column(Text)

    table_catalog: Mapped["TableCatalog"] = relationship(back_populates="dataset")
    owner: Mapped["User"] = relationship(back_populates="datasets")
    tags: Mapped[list["Tag"]] = relationship(
        secondary="dataset_tags", back_populates="datasets"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="dataset")