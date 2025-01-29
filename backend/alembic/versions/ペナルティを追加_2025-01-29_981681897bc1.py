"""“ペナルティを追加”

Revision ID: 981681897bc1
Revises: d858ef56f730
Create Date: 2025-01-29 21:15:13.234909+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '981681897bc1'
down_revision: Union[str, None] = 'd858ef56f730'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('incomes', sa.Column('penalty', sa.Float(
        precision=3, asdecimal=1), server_default='0', nullable=True))
    op.alter_column('incomes', 'year_month',
                    existing_type=mysql.CHAR(length=7),
                    nullable=False)
    op.alter_column('incomes', 'salary',
                    existing_type=mysql.FLOAT(),
                    nullable=False)
    op.alter_column('incomes', 'bonus',
                    existing_type=mysql.FLOAT(),
                    server_default='0', nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('incomes', 'bonus',
                    existing_type=mysql.FLOAT(),
                    nullable=True)
    op.alter_column('incomes', 'salary',
                    existing_type=mysql.FLOAT(),
                    nullable=True)
    op.alter_column('incomes', 'year_month',
                    existing_type=mysql.CHAR(length=7),
                    nullable=True)
    op.drop_column('incomes', 'penalty')
    # ### end Alembic commands ###
