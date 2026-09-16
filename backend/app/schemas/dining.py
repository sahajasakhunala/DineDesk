from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class ReservationBase(BaseModel):
    start_time: datetime
    end_time: datetime
    guest_count: int

class ReservationCreate(ReservationBase):
    table_id: UUID
    customer_id: UUID

class ReservationUpdate(BaseModel):
    table_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    guest_count: Optional[int] = None
    status: Optional[str] = None

class ReservationResponse(ReservationBase):
    id: UUID
    table_id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DiningSessionBase(BaseModel):
    guest_count: int

class DiningSessionCreate(DiningSessionBase):
    table_id: UUID
    reservation_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None

class DiningSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    guest_count: Optional[int] = None
    status: Optional[str] = None

class DiningSessionResponse(DiningSessionBase):
    id: UUID
    table_id: UUID
    reservation_id: Optional[UUID]
    customer_id: Optional[UUID]
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
