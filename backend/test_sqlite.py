import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Import all models to register them
from app.models.restaurant import Branch, DiningArea, TableEntity
from app.models.users import Role, UserAccount, Customer
from app.models.menu import MenuCategory, MenuItem
from app.models.billing import Discount, Bill, BillItem, Payment, DiscountApplication
from app.models.dining import Reservation, DiningSession
from app.models.orders import CustomerOrder, OrderItem, OrderStatusHistory
from app.models.kitchen import KitchenTicket, KitchenTicketItem

sqlite_url = "sqlite:///./dinedesk.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

print("Creating SQLite tables...")
Base.metadata.create_all(bind=engine)
print("SQLite tables created successfully!")
