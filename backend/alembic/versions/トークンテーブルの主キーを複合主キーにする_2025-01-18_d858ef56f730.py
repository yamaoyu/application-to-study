"""“トークンテーブルの主キーを複合主キーにする”

Revision ID: d858ef56f730
Revises: 8d3d93cec773
Create Date: 2025-01-18 18:15:54.682318+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd858ef56f730'
down_revision: Union[str, None] = '8d3d93cec773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('tokens_ibfk_1', 'tokens', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'tokens', type_='primary')
    op.create_primary_key('PRIMARY', 'tokens', ['username', 'device'])
    op.create_foreign_key('tokens_ibfk_1', 'tokens', 'users', ['username'], ['username'])


def downgrade() -> None:
    op.drop_constraint('tokens_ibfk_1', 'tokens', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'tokens', type_='primary')
    op.create_primary_key('PRIMARY', 'tokens', ['username'])
    op.create_foreign_key('tokens_ibfk_1', 'tokens', 'users', ['username'], ['username'])
