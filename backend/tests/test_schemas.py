from app.schemas.users import UserAccountCreate, UserAccountResponse, CustomerCreate
from pydantic import ValidationError
import pytest
from uuid import uuid4

def test_user_account_create_schema_requires_password():
    with pytest.raises(ValidationError):
        UserAccountCreate(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            role_id=1,
            branch_id=uuid4()
            # Missing password
        )

def test_user_account_response_hides_password():
    # The response schema should never expose the password or hash
    assert "password" not in UserAccountResponse.model_fields
    assert "password_hash" not in UserAccountResponse.model_fields

def test_customer_create_hides_ids():
    # Clients should not be able to set id, created_at, or updated_at when creating
    assert "id" not in CustomerCreate.model_fields
    assert "created_at" not in CustomerCreate.model_fields
    assert "updated_at" not in CustomerCreate.model_fields
