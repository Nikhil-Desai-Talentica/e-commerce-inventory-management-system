# app/models/sku.py
from decimal import Decimal

from sqlalchemy import Integer, String, Text, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SKU(Base):
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "name",
            name="uq_sku_product_name",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    product: Mapped["Product"] = relationship(
        back_populates="skus",
        lazy="selectin",
    )
