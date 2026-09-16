from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class BranchBase(BaseModel):
    name: str
    address: str
    phone: str

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class BranchResponse(BranchBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DiningAreaBase(BaseModel):
    name: str

class DiningAreaCreate(DiningAreaBase):
    branch_id: UUID

class DiningAreaUpdate(BaseModel):
    name: Optional[str] = None

class DiningAreaResponse(DiningAreaBase):
    id: UUID
    branch_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TableEntityBase(BaseModel):
    table_number: str
    capacity: int
    is_active: bool = True

class TableEntityCreate(TableEntityBase):
    area_id: UUID

class TableEntityUpdate(BaseModel):
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None

class TableEntityResponse(TableEntityBase):
    id: UUID
    area_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
