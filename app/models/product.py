# app/models/product.py
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("category.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    category: Mapped["Category"] = relationship(
        back_populates="products",
        lazy="selectin",
    )