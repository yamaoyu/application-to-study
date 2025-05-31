"""todoの詳細を登録できるようにする

Revision ID: e7631fb12762
Revises: 4e7c8338595c
Create Date: 2025-05-11 02:02:52.709343+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7631fb12762'
down_revision: Union[str, None] = '4e7c8338595c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('action', 'todos', type_='unique')
    op.alter_column('todos', 'action', new_column_name='title',
                    existing_type=sa.String(32))
    op.add_column('todos', sa.Column('detail', sa.String(200), nullable=True))


def downgrade() -> None:
    op.create_unique_constraint('action', 'todos', ['action', 'username'])
    op.alter_column('todos', 'title', new_column_name='action',
                    existing_type=sa.String(32))
    op.drop_column('todos', 'detail')
