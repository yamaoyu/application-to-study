"""“ボーナス、ペナルティを日ごとに保持”

Revision ID: 6e3b606c4ed8
Revises: 981681897bc1
Create Date: 2025-02-02 17:55:45.373416+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6e3b606c4ed8'
down_revision: Union[str, None] = '981681897bc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('bonus', sa.Float(), server_default='0', nullable=True))
    op.add_column('activities', sa.Column('penalty', sa.Float(), server_default='0', nullable=True))
    op.alter_column('incomes', 'bonus', new_column_name='total_bonus',
                    server_default='0', existing_type=sa.Float())
    op.alter_column('incomes', 'penalty', new_column_name='total_penalty',
                    server_default='0', existing_type=sa.Float())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('incomes', 'total_bonus', new_column_name='bonus', existing_type=sa.Float())
    op.alter_column('incomes', 'total_penalty', new_column_name='penalty', existing_type=sa.Float())
    op.drop_column('activities', 'penalty')
    op.drop_column('activities', 'bonus')
    # ### end Alembic commands ###
