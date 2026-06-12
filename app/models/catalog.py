from sqlalchemy import ForeignKey, Integer, String, Text, JSON, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, TimestampMixin, SensitivityLevel


class TableCatalog(Base, TimestampMixin):
    __tablename__ = "table_catalogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    datasource_id: Mapped[int] = mapped_column(ForeignKey("datasources.id"))
    scan_job_id: Mapped[int] = mapped_column(ForeignKey("scan_jobs.id"))
    table_name: Mapped[str] = mapped_column(String(255))
    row_count: Mapped[int | None] = mapped_column(Integer)

    datasource: Mapped["DataSource"] = relationship(back_populates="tables")
    scan_job: Mapped["ScanJob"] = relationship(back_populates="tables")
    columns: Mapped[list["ColumnCatalog"]] = relationship(back_populates="table")
    dataset: Mapped["Dataset | None"] = relationship(back_populates="table_catalog", uselist=False)


class ColumnCatalog(Base, TimestampMixin):
    __tablename__ = "column_catalogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table_catalogs.id"))
    column_name: Mapped[str] = mapped_column(String(255))
    declared_type: Mapped[str] = mapped_column(String(100))

    profile: Mapped[dict] = mapped_column(JSON, default=dict)

    sensitivity_level: Mapped[SensitivityLevel] = mapped_column(
        Enum(SensitivityLevel), default=SensitivityLevel.NONE
    )
    sensitivity_reason: Mapped[str | None] = mapped_column(Text)

    semantic_type: Mapped[str | None] = mapped_column(String(50))
    valid_ratio: Mapped[float | None] = mapped_column(Float)
    enrichment_source: Mapped[str | None] = mapped_column(String(100))

    table: Mapped["TableCatalog"] = relationship(back_populates="columns")