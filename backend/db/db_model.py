from sqlalchemy import (Column, Integer, Float, Date, Boolean, Enum,
                        CHAR, VARCHAR, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from db.database import Base, engine


class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    target_time = Column(Float(3, 1))
    actual_time = Column(Float(3, 1), default=0)
    is_achieved = Column(Boolean, default=False)
    username = Column(VARCHAR(16), ForeignKey("users.username"), nullable=False)
    __table_args__ = (UniqueConstraint(date, username),)

    user = relationship('User', back_populates='activities')


class Earning(Base):
    __tablename__ = "earnings"
    income_id = Column(Integer, primary_key=True, autoincrement=True)
    year_month = Column(CHAR(7))
    monthly_income = Column(Float(4, 1))
    bonus = Column(Float(3, 1))
    username = Column(VARCHAR(16), ForeignKey("users.username"))
    __table_args__ = (UniqueConstraint(year_month, username),)

    user = relationship('User', back_populates='earnings')


class Todo(Base):
    __tablename__ = "todos"
    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(VARCHAR(32), nullable=False)
    status = Column(Boolean, default=False)
    username = Column(VARCHAR(16), ForeignKey("users.username"), nullable=False)
    __table_args__ = (UniqueConstraint(action, username),)

    user = relationship('User', back_populates='todos')


class User(Base):
    __tablename__ = "users"
    username = Column(VARCHAR(16), primary_key=True)
    password = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(32), unique=True)
    role = Column(Enum("admin", "general"), default="general")

    earnings = relationship('Earning', back_populates='user')
    todos = relationship('Todo', back_populates='user')
    activities = relationship('Activity', back_populates='user')
    tokens = relationship('Token', back_populates='user')


class Token(Base):
    __tablename__ = "tokens"
    username = Column(VARCHAR(16), ForeignKey("users.username"), primary_key=True)
    token = Column(VARCHAR(256))
    expires_at = Column(Date, nullable=False)
    status = Column(Boolean, default=True)

    user = relationship('User', back_populates='tokens')


class Inquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum("要望", "エラー報告", "その他"), nullable=False)
    detail = Column(VARCHAR(256), nullable=False)
    date = Column(Date, nullable=False)
    priority = Column(Enum("高", "中", "低"), default="低")
    is_checked = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
