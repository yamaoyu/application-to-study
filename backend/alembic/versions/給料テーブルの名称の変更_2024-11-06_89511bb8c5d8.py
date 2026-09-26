"""給料テーブルの名称の変更

Revision ID: 89511bb8c5d8
Revises:
Create Date: 2024-11-06 23:25:52.395801+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Float


# revision identifiers, used by Alembic.
revision: str = '89511bb8c5d8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alembic導入前から存在していたテーブルを、新規DBの場合だけ作成する。
    # 既存DBではこの時点でearningsなどが存在するため、従来どおり変更だけを適用する。
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "earnings" not in table_names:
        op.create_table(
            "users",
            sa.Column("username", sa.VARCHAR(16), primary_key=True),
            sa.Column("password", sa.CHAR(60), nullable=False),
            sa.Column("email", sa.VARCHAR(32), nullable=True),
            sa.Column("role", sa.Enum("admin", "general"), nullable=True),
        )
        op.create_table(
            "earnings",
            sa.Column("income_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("year_month", sa.CHAR(7), nullable=True),
            sa.Column("monthly_income", sa.Float(4), nullable=True),
            sa.Column("bonus", sa.Float(3), nullable=True),
            sa.Column("username", sa.VARCHAR(16), nullable=True),
            sa.ForeignKeyConstraint(["username"], ["users.username"]),
            sa.UniqueConstraint("year_month", "username", name="year_month"),
        )
        op.create_table(
            "todos",
            sa.Column("todo_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("action", sa.VARCHAR(32), nullable=False),
            sa.Column("status", sa.Boolean(), nullable=True),
            sa.Column("username", sa.VARCHAR(16), nullable=False),
            sa.ForeignKeyConstraint(["username"], ["users.username"]),
            sa.UniqueConstraint("action", "username", name="action"),
        )
        op.create_table(
            "activities",
            sa.Column("activity_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("date", sa.Date(), nullable=True),
            sa.Column("target_time", sa.Float(3), nullable=True),
            sa.Column("actual_time", sa.Float(3), nullable=True),
            sa.Column("is_achieved", sa.Boolean(), nullable=True),
            sa.Column("username", sa.VARCHAR(16), nullable=False),
            sa.ForeignKeyConstraint(["username"], ["users.username"]),
            sa.UniqueConstraint("date", "username", name="date"),
        )
        op.create_table(
            "tokens",
            sa.Column("username", sa.VARCHAR(16), primary_key=True),
            sa.Column("token", sa.VARCHAR(256), nullable=True),
            sa.Column("expires_at", sa.Date(), nullable=False),
            sa.Column("status", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(
                ["username"], ["users.username"], name="tokens_ibfk_1"
            ),
        )
        op.create_table(
            "inquiries",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "category",
                sa.Enum("要望", "エラー報告", "その他"),
                nullable=False,
            ),
            sa.Column("detail", sa.VARCHAR(256), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("priority", sa.Enum("高", "中", "低"), nullable=True),
            sa.Column("is_checked", sa.Boolean(), nullable=True),
        )

    op.rename_table(old_table_name="earnings", new_table_name="incomes")
    op.alter_column(table_name='incomes', column_name='monthly_income',
                    new_column_name='salary', existing_type=Float(precision=4, asdecimal=True))


def downgrade() -> None:
    op.rename_table(old_table_name="incomes", new_table_name="earnings")
    op.alter_column(table_name='earnings', column_name='salary',
                    new_column_name='monthly_income', existing_type=Float(precision=4, asdecimal=True))
