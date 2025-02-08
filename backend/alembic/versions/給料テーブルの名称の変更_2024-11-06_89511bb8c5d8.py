"""給料テーブルの名称の変更

Revision ID: 89511bb8c5d8
Revises:
Create Date: 2024-11-06 23:25:52.395801+09:00

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Float


# revision identifiers, used by Alembic.
revision: str = '89511bb8c5d8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table(old_table_name="earnings", new_table_name="incomes")
    op.alter_column(table_name='incomes', column_name='monthly_income',
                    new_column_name='salary', existing_type=Float(4, 1))


def downgrade() -> None:
    op.rename_table(old_table_name="incomes", new_table_name="earnings")
    op.alter_column(table_name='earnings', column_name='salary',
                    new_column_name='monthly_income', existing_type=Float(4, 1))
