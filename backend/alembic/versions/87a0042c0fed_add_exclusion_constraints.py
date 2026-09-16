"""Add exclusion constraints

Revision ID: 87a0042c0fed
Revises: 88edc4091ff8
Create Date: 2026-08-21 12:35:24.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87a0042c0fed'
down_revision: Union[str, Sequence[str], None] = '88edc4091ff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ensure btree_gist extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
    
    # 2. Add reservation exclusion constraint
    op.execute("""
        ALTER TABLE reservation ADD CONSTRAINT excl_reservation_overlap
        EXCLUDE USING gist (
            table_id WITH =,
            tstzrange(start_time, end_time) WITH &&
        ) WHERE (status IN ('PENDING', 'CONFIRMED'));
    """)

    # 3. Add dining_session exclusion constraint
    op.execute("""
        ALTER TABLE dining_session ADD CONSTRAINT excl_session_overlap
        EXCLUDE USING gist (
            table_id WITH =,
            tstzrange(start_time, COALESCE(end_time, 'infinity')) WITH &&
        ) WHERE (status = 'ACTIVE');
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE dining_session DROP CONSTRAINT IF EXISTS excl_session_overlap;")
    op.execute("ALTER TABLE reservation DROP CONSTRAINT IF EXISTS excl_reservation_overlap;")
