from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class MenuCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class MenuCategoryCreate(MenuCategoryBase):
    pass

class MenuCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class MenuCategoryResponse(MenuCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    current_price: Decimal
    is_active: bool = True

class MenuItemCreate(MenuItemBase):
    category_id: int

class MenuItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[Decimal] = None
    is_active: Optional[bool] = None

class MenuItemResponse(MenuItemBase):
    id: UUID
    category_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
