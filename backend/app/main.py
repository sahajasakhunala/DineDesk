from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db, engine
from app.models.base import Base

# Ensure all tables are created
Base.metadata.create_all(bind=engine)

from app.api.v1.auth import router as auth_router
from app.api.v1.restaurant import router as restaurant_router
from app.api.v1.reservations import router as reservations_router
from app.api.v1.dining import router as dining_router
from app.api.v1.menu import router as menu_router
from app.api.v1.orders import router as orders_router
from app.api.v1.kitchen import router as kitchen_router
from app.api.v1.billing import router as billing_router
from app.api.v1.reports import router as reports_router
from app.api.v1.documents import router as documents_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Restaurant Table Reservation and Food Service Management System API",
    version="1.0.0"
)

# Enable CORS for local frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 Routers
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(restaurant_router, prefix=api_v1_prefix)
app.include_router(reservations_router, prefix=api_v1_prefix)
app.include_router(dining_router, prefix=api_v1_prefix)
app.include_router(menu_router, prefix=api_v1_prefix)
app.include_router(orders_router, prefix=api_v1_prefix)
app.include_router(kitchen_router, prefix=api_v1_prefix)
app.include_router(billing_router, prefix=api_v1_prefix)
app.include_router(reports_router, prefix=api_v1_prefix)
app.include_router(documents_router, prefix=api_v1_prefix)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": api_v1_prefix
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "details": str(e)}
