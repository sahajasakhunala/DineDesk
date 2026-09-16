import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Role(Base):
    __tablename__ = 'role'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    users: Mapped[List["UserAccount"]] = relationship("UserAccount", back_populates="role")


class UserAccount(Base):
    __tablename__ = 'user_account'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('branch.id'), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="users")
    orders: Mapped[List["CustomerOrder"]] = relationship("CustomerOrder", back_populates="user")


class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="customer")
    dining_sessions: Mapped[List["DiningSession"]] = relationship("DiningSession", back_populates="customer")
