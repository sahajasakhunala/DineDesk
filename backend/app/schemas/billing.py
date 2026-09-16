from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class BillBase(BaseModel):
    pass

class BillCreate(BillBase):
    session_id: UUID

class BillUpdate(BaseModel):
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None

class BillResponse(BillBase):
    id: UUID
    session_id: UUID
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaymentBase(BaseModel):
    amount: Decimal
    payment_method: str
    transaction_ref: Optional[str] = None

class PaymentCreate(PaymentBase):
    bill_id: UUID

class PaymentUpdate(BaseModel):
    status: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: UUID
    bill_id: UUID
    amount: Decimal
    payment_method: str
    status: str
    transaction_ref: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
