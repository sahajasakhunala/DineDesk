import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.restaurant import Branch, DiningArea
from app.schemas.restaurant import BranchResponse, DiningAreaResponse
from app.services.dining_service import get_tables_with_status

router = APIRouter(prefix="/restaurant", tags=["Restaurant Structure"])

@router.get("/branches", response_model=List[BranchResponse])
def get_branches(db: Session = Depends(get_db)):
    return db.query(Branch).order_by(Branch.name.asc()).all()

@router.get("/areas", response_model=List[DiningAreaResponse])
def get_dining_areas(
    branch_id: Optional[uuid.UUID] = Query(None, description="Filter areas by branch ID"),
    db: Session = Depends(get_db)
):
    query = db.query(DiningArea)
    if branch_id:
        query = query.filter(DiningArea.branch_id == branch_id)
    return query.order_by(DiningArea.name.asc()).all()

from datetime import datetime

@router.get("/tables")
def get_tables(
    area_id: Optional[uuid.UUID] = Query(None, description="Filter tables by dining area"),
    status: Optional[str] = Query(None, description="Filter tables by status (AVAILABLE, RESERVED, OCCUPIED)"),
    start_time: Optional[datetime] = Query(None, description="Check availability for start time"),
    end_time: Optional[datetime] = Query(None, description="Check availability for end time"),
    db: Session = Depends(get_db)
):
    return get_tables_with_status(db, area_id=area_id, status_filter=status, check_start=start_time, check_end=end_time)

from pydantic import BaseModel
from fastapi import HTTPException, status
from app.models.restaurant import TableEntity

class CreateTableRequest(BaseModel):
    table_number: str
    capacity: int
    area_id: Optional[uuid.UUID] = None
    area_name: Optional[str] = None

@router.post("/tables")
def create_table(req: CreateTableRequest, db: Session = Depends(get_db)):
    area = None
    if req.area_id:
        area = db.query(DiningArea).filter(DiningArea.id == req.area_id).first()
    elif req.area_name:
        area = db.query(DiningArea).filter(DiningArea.name.ilike(f"%{req.area_name}%")).first()

    if not area:
        area = db.query(DiningArea).first()
        if not area:
            branch = db.query(Branch).first()
            area = DiningArea(name="Main Dining Hall", branch_id=branch.id if branch else uuid.uuid4())
            db.add(area)
            db.commit()
            db.refresh(area)

    t_num = req.table_number.strip().upper()
    existing = db.query(TableEntity).filter(TableEntity.table_number == t_num).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Table {t_num} already exists.")

    new_table = TableEntity(
        table_number=t_num,
        capacity=max(1, req.capacity),
        area_id=area.id,
        is_active=True
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return {
        "id": str(new_table.id),
        "table_number": new_table.table_number,
        "capacity": new_table.capacity,
        "area_name": area.name,
        "status": "AVAILABLE"
    }

@router.delete("/tables/{table_id}")
def delete_table(table_id: uuid.UUID, db: Session = Depends(get_db)):
    table = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found.")

    from app.models.dining import Reservation, DiningSession
    db.query(Reservation).filter(Reservation.table_id == table_id).delete(synchronize_session=False)
    db.query(DiningSession).filter(DiningSession.table_id == table_id).delete(synchronize_session=False)

    db.delete(table)
    db.commit()
    return {"status": "DELETED", "id": str(table_id), "message": f"Table {table.table_number} permanently deleted."}

