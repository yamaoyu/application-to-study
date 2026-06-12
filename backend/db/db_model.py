from sqlalchemy import (Column, Integer, Float, Date, Boolean, Enum,
                        CHAR, VARCHAR, ForeignKey, UniqueConstraint, PrimaryKeyConstraint)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.database import Base
import datetime
from typing import Optional


class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    target_time = Column(Float)
    actual_time = Column(Float, default=0)
    status = Column(Enum("pending", "success", "failure"), server_default="pending")
    bonus = Column(Float, server_default="0")
    penalty = Column(Float, server_default="0")
    username = Column(VARCHAR(16), ForeignKey("users.username"), nullable=False)
    __table_args__ = (UniqueConstraint(date, username),)

    user = relationship('User', back_populates='activities')


class Income(Base):
    __tablename__ = "incomes"
    income_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    income_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    username: Mapped[str] = mapped_column(VARCHAR(16), ForeignKey("users.username"))
    __table_args__ = (UniqueConstraint(income_month, username),)

    user = relationship('User', back_populates='incomes')


class Todo(Base):
    __tablename__ = "todos"
    todo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    due: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    username: Mapped[str] = mapped_column(VARCHAR(16), ForeignKey("users.username"), nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)

    user = relationship('User', back_populates='todos')


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(VARCHAR(16), primary_key=True)
    password: Mapped[str] = mapped_column(CHAR(60), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(VARCHAR(32), nullable=True, unique=True)
    role: Mapped[str] = mapped_column(Enum("admin", "general"), default="general", nullable=False)

    incomes = relationship('Income', back_populates='user')
    todos = relationship('Todo', back_populates='user')
    activities = relationship('Activity', back_populates='user')
    tokens = relationship('Token', back_populates='user')


class Token(Base):
    __tablename__ = "tokens"
    username: Mapped[str] = mapped_column(VARCHAR(16), ForeignKey("users.username"), nullable=False)
    device_id: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    token: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    expires_at: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    __table_args__ = (PrimaryKeyConstraint(username, device_id),)

    user = relationship('User', back_populates='tokens')


class Inquiry(Base):
    __tablename__ = "inquiries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(Enum("要望", "エラー報告", "その他"), nullable=False)
    detail: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    priority: Mapped[str | None] = mapped_column(
        Enum("高", "中", "低"),
        default="低",
        nullable=True,
    )
    is_checked: Mapped[bool | None] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )
