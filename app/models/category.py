from sqlalchemy import String, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, TimestampMixin

category_datasource = Table(
    "category_datasource",
    Base.metadata,
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("datasource_id", ForeignKey("datasources.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(500))

    datasources: Mapped[list["DataSource"]] = relationship(
        secondary=category_datasource, back_populates="categories"
    )