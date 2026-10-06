import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.menu import MenuCategory, MenuItem
from app.schemas.menu import MenuCategoryResponse, MenuItemCreate, MenuItemResponse
from app.services.auth_service import require_role

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.get("/categories", response_model=List[MenuCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(MenuCategory).order_by(MenuCategory.name.asc()).all()

@router.get("/items")
def get_menu_items(
    category_id: Optional[int] = Query(None, description="Filter items by category ID"),
    category: Optional[str] = Query(None, description="Filter items by category name"),
    is_active: Optional[bool] = Query(True, description="Filter items by active status"),
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem).join(MenuCategory)
    if is_active is not None:
        query = query.filter(MenuItem.is_active == is_active)
    if category_id is not None:
        query = query.filter(MenuItem.category_id == category_id)
    if category is not None and category.lower() != "all":
        query = query.filter(MenuCategory.name.ilike(f"%{category}%"))

    items = query.order_by(MenuItem.name.asc()).all()
    return [
        {
            "id": str(item.id),
            "category_id": item.category_id,
            "category": item.category.name if item.category else "Uncategorized",
            "name": item.name,
            "description": item.description,
            "current_price": float(item.current_price),
            "price": float(item.current_price),  # For frontend compatibility
            "image_url": item.image_url,
            "is_active": item.is_active
        }
        for item in items
    ]

@router.post("/items", response_model=MenuItemResponse)
def create_menu_item(
    item_in: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("MANAGER", "ADMIN"))
):
    new_item = MenuItem(
        category_id=item_in.category_id,
        name=item_in.name,
        description=item_in.description,
        current_price=item_in.current_price,
        image_url=item_in.image_url,
        is_active=item_in.is_active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
