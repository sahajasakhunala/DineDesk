import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Reservation(Base):
    __tablename__ = 'reservation'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    table_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('table_entity.id'), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('customer.id'), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default='PENDING', nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='chk_reservation_time'),
        CheckConstraint('guest_count > 0', name='chk_reservation_guests'),
        CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'NO_SHOW', 'COMPLETED')", name='chk_reservation_status'),
    )

    table: Mapped["TableEntity"] = relationship("TableEntity", back_populates="reservations")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="reservations")


class DiningSession(Base):
    __tablename__ = 'dining_session'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    table_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('table_entity.id'), nullable=False, index=True)
    reservation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('reservation.id'), nullable=True, index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('customer.id'), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default='ACTIVE', nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('guest_count > 0', name='chk_session_guests'),
        CheckConstraint("status IN ('ACTIVE', 'COMPLETED')", name='chk_session_status'),
        CheckConstraint(
            "(status = 'ACTIVE' AND end_time IS NULL) OR (status = 'COMPLETED' AND end_time IS NOT NULL)",
            name='chk_session_end_time'
        ),
    )

    table: Mapped["TableEntity"] = relationship("TableEntity", back_populates="dining_sessions")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="dining_sessions")
    orders: Mapped[List["CustomerOrder"]] = relationship("CustomerOrder", back_populates="session")
    bill: Mapped[Optional["Bill"]] = relationship("Bill", back_populates="session", uselist=False)
