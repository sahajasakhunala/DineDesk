import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class KitchenTicket(Base):
    __tablename__ = 'kitchen_ticket'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('customer_order.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), server_default='PENDING', nullable=False)
    prep_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ready_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'IN_PROGRESS', 'READY')", name='chk_kitchen_ticket_status'),
    )

    order: Mapped["CustomerOrder"] = relationship("CustomerOrder", back_populates="kitchen_ticket")
    items: Mapped[List["KitchenTicketItem"]] = relationship("KitchenTicketItem", back_populates="ticket", cascade="all, delete-orphan")


class KitchenTicketItem(Base):
    __tablename__ = 'kitchen_ticket_item'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('kitchen_ticket.id', ondelete='CASCADE'), nullable=False)
    order_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order_item.id', ondelete='CASCADE'), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), server_default='PENDING', nullable=False)

    __table_args__ = (
        UniqueConstraint('ticket_id', 'order_item_id', name='uq_kitchen_ticket_item'),
        CheckConstraint("status IN ('PENDING', 'PREPARING', 'COMPLETED', 'CANCELLED')", name='chk_kt_item_status'),
    )

    ticket: Mapped["KitchenTicket"] = relationship("KitchenTicket", back_populates="items")
