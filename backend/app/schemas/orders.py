from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class OrderItemBase(BaseModel):
    quantity: int
    unit_price: Decimal
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    item_id: UUID

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    special_requests: Optional[str] = None

class OrderItemResponse(OrderItemBase):
    id: UUID
    order_id: UUID
    item_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CustomerOrderBase(BaseModel):
    pass

class CustomerOrderCreate(CustomerOrderBase):
    session_id: UUID
    user_id: UUID

class CustomerOrderUpdate(BaseModel):
    status: Optional[str] = None

class CustomerOrderResponse(CustomerOrderBase):
    id: UUID
    session_id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
