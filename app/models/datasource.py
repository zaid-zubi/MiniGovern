from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, TimestampMixin


class DataSource(Base, TimestampMixin):
    __tablename__ = "datasources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(default=3306)
    database: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    encrypted_password: Mapped[str] = mapped_column(Text)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="datasources")
    categories: Mapped[list["Category"]] = relationship(
        secondary="category_datasource", back_populates="datasources"
    )
    scan_jobs: Mapped[list["ScanJob"]] = relationship(back_populates="datasource")
    tables: Mapped[list["TableCatalog"]] = relationship(back_populates="datasource")
