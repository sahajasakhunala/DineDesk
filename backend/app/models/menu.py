import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Numeric, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class MenuCategory(Base):
    __tablename__ = 'menu_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["MenuItem"]] = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = 'menu_item'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[int] = mapped_column(ForeignKey('menu_category.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('current_price >= 0', name='chk_menu_item_price'),
    )

    category: Mapped["MenuCategory"] = relationship("MenuCategory", back_populates="items")
