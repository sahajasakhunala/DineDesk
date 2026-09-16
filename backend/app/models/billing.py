import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Numeric, ForeignKey, DateTime, CheckConstraint, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Bill(Base):
    __tablename__ = 'bill'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('dining_session.id'), unique=True, nullable=False, index=True)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), server_default='0', nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), server_default='0', nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), server_default='0', nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default='UNPAID', nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('subtotal >= 0', name='chk_bill_subtotal'),
        CheckConstraint('tax_amount >= 0', name='chk_bill_tax'),
        CheckConstraint('total_amount >= 0', name='chk_bill_total'),
        CheckConstraint("status IN ('UNPAID', 'PARTIAL', 'PAID', 'VOIDED')", name='chk_bill_status'),
    )

    session: Mapped["DiningSession"] = relationship("DiningSession", back_populates="bill")
    items: Mapped[List["BillItem"]] = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    discounts: Mapped[List["DiscountApplication"]] = relationship("DiscountApplication", back_populates="bill", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="bill", cascade="all, delete-orphan")


class BillItem(Base):
    __tablename__ = 'bill_item'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bill.id', ondelete='CASCADE'), nullable=False)
    order_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order_item.id'), nullable=False)
    item_name_snapshot: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), Computed('quantity * unit_price', persisted=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_bill_item_qty'),
        CheckConstraint('unit_price >= 0', name='chk_bill_item_price'),
    )

    bill: Mapped["Bill"] = relationship("Bill", back_populates="items")


class Discount(Base):
    __tablename__ = 'discount'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    max_discount_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("discount_type IN ('FIXED', 'PERCENTAGE')", name='chk_discount_type'),
        CheckConstraint("(discount_type = 'FIXED' AND value > 0) OR (discount_type = 'PERCENTAGE' AND value > 0 AND value <= 100)", name='chk_discount_value'),
        CheckConstraint('max_discount_amount > 0', name='chk_discount_max'),
    )


class DiscountApplication(Base):
    __tablename__ = 'discount_application'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bill.id', ondelete='CASCADE'), nullable=False, index=True)
    discount_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('discount.id'), nullable=False, index=True)
    authorized_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user_account.id'), nullable=False)
    discount_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    discount_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('discount_amount > 0', name='chk_da_amount'),
        CheckConstraint('discount_percentage > 0 AND discount_percentage <= 100', name='chk_da_percentage'),
        CheckConstraint(
            '(discount_amount IS NOT NULL AND discount_percentage IS NULL) OR '
            '(discount_amount IS NULL AND discount_percentage IS NOT NULL)',
            name='chk_da_exclusive'
        ),
    )

    bill: Mapped["Bill"] = relationship("Bill", back_populates="discounts")
    discount_rule: Mapped["Discount"] = relationship("Discount")


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('bill.id', ondelete='CASCADE'), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('amount > 0', name='chk_payment_amount'),
        CheckConstraint("payment_method IN ('CASH', 'CARD', 'ONLINE', 'WALLET')", name='chk_payment_method'),
        CheckConstraint("status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')", name='chk_payment_status'),
    )

    bill: Mapped["Bill"] = relationship("Bill", back_populates="payments")
