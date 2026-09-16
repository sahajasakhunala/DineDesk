from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserAccountBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserAccountCreate(UserAccountBase):
    role_id: int
    branch_id: UUID
    password: str

class UserAccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    branch_id: Optional[UUID] = None

class UserAccountResponse(UserAccountBase):
    id: UUID
    role_id: int
    branch_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
