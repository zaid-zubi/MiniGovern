from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, JobStatus, TimestampMixin


class ScanJob(Base, TimestampMixin):
    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    datasource_id: Mapped[int] = mapped_column(ForeignKey("datasources.id"))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    error_message: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[dict | None] = mapped_column(JSON)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    datasource: Mapped["DataSource"] = relationship(back_populates="scan_jobs")
    tables: Mapped[list["TableCatalog"]] = relationship(back_populates="scan_job")
