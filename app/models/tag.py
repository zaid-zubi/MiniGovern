from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base, TimestampMixin

dataset_tags = Table(
    "dataset_tags",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    datasets: Mapped[list["Dataset"]] = relationship(
        secondary=dataset_tags, back_populates="tags"
    )