import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.users import UserAccount, Customer
from app.schemas.users import UserAccountResponse, CustomerCreate, CustomerResponse
from app.services.auth_service import authenticate_user, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    branch_id: uuid.UUID

class CustomerRegisterRequest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role_name = user.role.name if user.role else "STAFF"
    token = create_access_token(data={"sub": str(user.id), "role": role_name})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=role_name,
        branch_id=user.branch_id
    )

@router.get("/me")
def get_me(current_user: UserAccount = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role.name if current_user.role else "STAFF",
        "branch_id": current_user.branch_id
    }

@router.post("/customer", response_model=CustomerResponse)
def register_or_get_customer(req: CustomerRegisterRequest, db: Session = Depends(get_db)):
    # Check if customer already exists by phone or email
    customer = None
    if req.phone:
        customer = db.query(Customer).filter(Customer.phone == req.phone).first()
    if not customer and req.email:
        customer = db.query(Customer).filter(Customer.email == req.email).first()

    # Split name into first and last name
    name_parts = req.name.strip().split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    if customer:
        if req.name and req.name.strip():
            customer.first_name = first_name
            customer.last_name = last_name
        if req.email:
            customer.email = req.email
        if req.phone and not customer.phone:
            customer.phone = req.phone
        db.commit()
        db.refresh(customer)
        return customer

    new_cust = Customer(
        first_name=first_name,
        last_name=last_name,
        phone=req.phone,
        email=req.email
    )
    db.add(new_cust)
    db.commit()
    db.refresh(new_cust)
    return new_cust
