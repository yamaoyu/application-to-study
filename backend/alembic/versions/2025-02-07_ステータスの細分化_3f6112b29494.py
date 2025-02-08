"""“ステータスの細分化”

Revision ID: 3f6112b29494
Revises: 6e3b606c4ed8
Create Date: 2025-02-07 20:48:46.775371+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f6112b29494'
down_revision: Union[str, None] = '6e3b606c4ed8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('activities', 'is_achieved', new_column_name='status',
                    server_default='pending', existing_type=sa.Enum('pending', 'success', 'failure'))
    op.execute(
        "UPDATE activities SET status = CASE WHEN actual_time >= target_time THEN 'success' "
        "WHEN bonus = 0 and penalty = 0 THEN 'pending' ELSE 'failure' END")


def downgrade() -> None:
    op.alter_column('activities', 'status', new_column_name='is_achieved',
                    server_default=False, existing_type=sa.Boolean)
    op.execute(
        "UPDATE activities SET is_achieved = CASE WHEN actual_time >= target_time THEN 1 ELSE 0 END")
