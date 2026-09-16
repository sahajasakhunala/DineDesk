import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Integer, Numeric, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class CustomerOrder(Base):
    __tablename__ = 'customer_order'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('dining_session.id'), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user_account.id'), nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default='PLACED', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('PLACED', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED', 'CANCELLED')", name='chk_order_status'),
    )

    session: Mapped["DiningSession"] = relationship("DiningSession", back_populates="orders")
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history: Mapped[List["OrderStatusHistory"]] = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    kitchen_ticket: Mapped[Optional["KitchenTicket"]] = relationship("KitchenTicket", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderStatusHistory(Base):
    __tablename__ = 'order_status_history'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('customer_order.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    order: Mapped["CustomerOrder"] = relationship("CustomerOrder", back_populates="status_history")


class OrderItem(Base):
    __tablename__ = 'order_item'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('customer_order.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('menu_item.id'), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    special_requests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_order_item_qty'),
        CheckConstraint('unit_price >= 0', name='chk_order_item_price'),
    )

    order: Mapped["CustomerOrder"] = relationship("CustomerOrder", back_populates="items")
