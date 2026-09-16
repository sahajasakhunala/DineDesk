import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection, join_transaction_mode="create_savepoint")
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# --- Reusable Test Fixtures ---

@pytest.fixture
def test_branch(db):
    from app.models.restaurant import Branch
    branch = Branch(name="Test Branch", address="123 Test St", phone="555-0101")
    db.add(branch)
    db.commit()
    return branch

@pytest.fixture
def test_area(db, test_branch):
    from app.models.restaurant import DiningArea
    area = DiningArea(branch_id=test_branch.id, name="Main Hall")
    db.add(area)
    db.commit()
    return area

@pytest.fixture
def test_table(db, test_area):
    from app.models.restaurant import TableEntity
    table = TableEntity(area_id=test_area.id, table_number="T1", capacity=4)
    db.add(table)
    db.commit()
    return table

@pytest.fixture
def test_customer(db):
    from app.models.users import Customer
    customer = Customer(first_name="John", last_name="Doe", phone="555-9999")
    db.add(customer)
    db.commit()
    return customer

@pytest.fixture
def test_user(db, test_branch):
    from app.models.users import Role, UserAccount
    role = Role(name="MANAGER")
    db.add(role)
    db.commit()
    user = UserAccount(
        role_id=role.id,
        branch_id=test_branch.id,
        first_name="Admin",
        last_name="User",
        email="admin@test.com",
        password_hash="hash"
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_menu_item(db):
    from app.models.menu import MenuCategory, MenuItem
    cat = MenuCategory(name="Mains")
    db.add(cat)
    db.commit()
    item = MenuItem(category_id=cat.id, name="Steak", current_price=25.00)
    db.add(item)
    db.commit()
    return item

@pytest.fixture
def test_session(db, test_table):
    from app.models.dining import DiningSession
    from datetime import datetime
    session = DiningSession(table_id=test_table.id, guest_count=2, status='ACTIVE', start_time=datetime.now())
    db.add(session)
    db.commit()
    return session

@pytest.fixture
def test_order(db, test_session, test_user):
    from app.models.orders import CustomerOrder
    order = CustomerOrder(session_id=test_session.id, user_id=test_user.id, status='PLACED')
    db.add(order)
    db.commit()
    return order

@pytest.fixture
def test_bill(db, test_session):
    from app.models.billing import Bill
    bill = Bill(session_id=test_session.id, subtotal=100, tax_amount=10, total_amount=110, status='UNPAID')
    db.add(bill)
    db.commit()
    return bill
