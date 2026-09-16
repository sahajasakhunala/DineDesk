import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Branch(Base):
    __tablename__ = 'branch'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    dining_areas: Mapped[List["DiningArea"]] = relationship("DiningArea", back_populates="branch", cascade="all, delete-orphan")
    users: Mapped[List["UserAccount"]] = relationship("UserAccount", back_populates="branch")


class DiningArea(Base):
    __tablename__ = 'dining_area'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('branch.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    branch: Mapped["Branch"] = relationship("Branch", back_populates="dining_areas")
    tables: Mapped[List["TableEntity"]] = relationship("TableEntity", back_populates="area", cascade="all, delete-orphan")


class TableEntity(Base):
    __tablename__ = 'table_entity'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    area_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('dining_area.id', ondelete='CASCADE'), nullable=False, index=True)
    table_number: Mapped[str] = mapped_column(String(20), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('area_id', 'table_number', name='uq_table_entity_area_number'),
        CheckConstraint('capacity > 0', name='chk_table_entity_capacity'),
    )

    area: Mapped["DiningArea"] = relationship("DiningArea", back_populates="tables")
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="table")
    dining_sessions: Mapped[List["DiningSession"]] = relationship("DiningSession", back_populates="table")
