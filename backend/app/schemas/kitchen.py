from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class KitchenTicketBase(BaseModel):
    pass

class KitchenTicketCreate(KitchenTicketBase):
    order_id: UUID

class KitchenTicketUpdate(BaseModel):
    status: Optional[str] = None
    prep_start_time: Optional[datetime] = None
    ready_time: Optional[datetime] = None

class KitchenTicketResponse(KitchenTicketBase):
    id: UUID
    order_id: UUID
    status: str
    prep_start_time: Optional[datetime]
    ready_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class KitchenTicketItemBase(BaseModel):
    pass

class KitchenTicketItemCreate(KitchenTicketItemBase):
    ticket_id: UUID
    order_item_id: UUID

class KitchenTicketItemUpdate(BaseModel):
    status: Optional[str] = None

class KitchenTicketItemResponse(KitchenTicketItemBase):
    id: UUID
    ticket_id: UUID
    order_item_id: UUID
    status: str
    model_config = ConfigDict(from_attributes=True)
