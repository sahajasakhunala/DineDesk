from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.core.database import get_db
from app.models.restaurant import TableEntity
from app.models.dining import DiningSession, Reservation
from app.models.orders import CustomerOrder, OrderItem
from app.models.kitchen import KitchenTicket
from app.models.billing import Bill, Payment, DiscountApplication
from app.models.menu import MenuItem, MenuCategory
from app.models.users import UserAccount
from app.services.dining_service import get_tables_with_status

router = APIRouter(prefix="/reports", tags=["Operational Reports"])

@router.get("/dashboard-summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    tables = get_tables_with_status(db)
    available_cnt = sum(1 for t in tables if t["status"] == "AVAILABLE")
    reserved_cnt = sum(1 for t in tables if t["status"] == "RESERVED")
    occupied_cnt = sum(1 for t in tables if t["status"] == "OCCUPIED")

    active_sessions_cnt = db.query(DiningSession).filter(DiningSession.status == "ACTIVE").count()
    pending_orders_cnt = db.query(CustomerOrder).filter(CustomerOrder.status.in_(["PLACED", "CONFIRMED"])).count()
    active_kitchen_tickets_cnt = db.query(KitchenTicket).filter(KitchenTicket.status.in_(["PENDING", "IN_PROGRESS"])).count()

    # Today's revenue from completed payments
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue_res = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == "COMPLETED",
        Payment.created_at >= today_start
    ).scalar()
    today_revenue = float(today_revenue_res or 0)

    # Total revenue all time
    total_revenue_res = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == "COMPLETED"
    ).scalar()

    return {
        "tables": {
            "total": len(tables),
            "available": available_cnt,
            "reserved": reserved_cnt,
            "occupied": occupied_cnt
        },
        "active_sessions": active_sessions_cnt,
        "pending_orders": pending_orders_cnt,
        "active_kitchen_tickets": active_kitchen_tickets_cnt,
        "today_revenue": round(today_revenue, 2),
        "total_revenue": round(float(total_revenue_res or 0), 2)
    }

@router.get("/daily-revenue")
def get_daily_revenue(db: Session = Depends(get_db)):
    records = db.query(
        func.date_trunc('day', Payment.created_at).label('pay_date'),
        func.count(Payment.id).label('tx_count'),
        func.sum(Payment.amount).label('total_revenue')
    ).filter(Payment.status == "COMPLETED").group_by('pay_date').order_by(text('pay_date DESC')).limit(30).all()

    return [
        {
            "date": r.pay_date.strftime('%Y-%m-%d') if r.pay_date else "N/A",
            "transaction_count": r.tx_count,
            "total_revenue": float(r.total_revenue or 0)
        }
        for r in records
    ]

@router.get("/item-sales")
def get_item_sales(db: Session = Depends(get_db)):
    records = db.query(
        MenuItem.name.label('item_name'),
        MenuCategory.name.label('category_name'),
        func.sum(OrderItem.quantity).label('total_qty'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
    ).join(MenuItem, OrderItem.item_id == MenuItem.id)\
     .join(MenuCategory, MenuItem.category_id == MenuCategory.id)\
     .join(CustomerOrder, OrderItem.order_id == CustomerOrder.id)\
     .filter(CustomerOrder.status != "CANCELLED")\
     .group_by(MenuItem.name, MenuCategory.name)\
     .order_by(text('total_qty DESC')).limit(20).all()

    return [
        {
            "item_name": r.item_name,
            "category": r.category_name,
            "units_sold": int(r.total_qty or 0),
            "total_sales": float(r.total_revenue or 0)
        }
        for r in records
    ]

@router.get("/table-turnover")
def get_table_turnover(db: Session = Depends(get_db)):
    records = db.query(
        TableEntity.table_number,
        TableEntity.capacity,
        func.count(DiningSession.id).label('session_count'),
        func.avg(
            func.extract('epoch', DiningSession.end_time - DiningSession.start_time) / 60
        ).label('avg_duration_minutes')
    ).outerjoin(DiningSession, TableEntity.id == DiningSession.table_id)\
     .group_by(TableEntity.table_number, TableEntity.capacity)\
     .order_by(TableEntity.table_number.asc()).all()

    return [
        {
            "table_number": r.table_number,
            "capacity": r.capacity,
            "total_sessions": r.session_count,
            "avg_duration_minutes": round(float(r.avg_duration_minutes or 0), 1)
        }
        for r in records
    ]

@router.get("/payment-methods")
def get_payment_methods(db: Session = Depends(get_db)):
    records = db.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('total')
    ).filter(Payment.status == "COMPLETED")\
     .group_by(Payment.payment_method)\
     .order_by(text('total DESC')).all()

    return [
        {
            "method": r.payment_method,
            "transaction_count": r.count,
            "total_amount": float(r.total or 0)
        }
        for r in records
    ]
