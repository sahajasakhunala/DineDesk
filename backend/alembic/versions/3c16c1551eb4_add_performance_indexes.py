"""add_performance_indexes

Revision ID: 3c16c1551eb4
Revises: 87a0042c0fed
Create Date: 2026-09-17 02:30:12.882135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c16c1551eb4'
down_revision: Union[str, Sequence[str], None] = '87a0042c0fed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_kitchen_ticket_status_created', 'kitchen_ticket', ['status', 'created_at'])
    op.create_index('ix_customer_order_status', 'customer_order', ['status'])
    op.create_index('ix_payment_created_at', 'payment', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_payment_created_at', table_name='payment')
    op.drop_index('ix_customer_order_status', table_name='customer_order')
    op.drop_index('ix_kitchen_ticket_status_created', table_name='kitchen_ticket')
