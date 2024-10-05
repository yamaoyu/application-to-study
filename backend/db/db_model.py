from sqlalchemy import (Column, Integer, Float, Date, Boolean, Enum,
                        CHAR, VARCHAR, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from db.database import Base, engine


class Activity(Base):
    __tablename__ = "activity"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    target_time = Column(Float(3, 1))
    actual_time = Column(Float(3, 1), default=0)
    is_achieved = Column(Boolean, default=False)
    username = Column(VARCHAR(16), ForeignKey("user.username"), nullable=False)
    __table_args__ = (UniqueConstraint(date, username),)

    user = relationship('User', back_populates='activity')


class Income(Base):
    __tablename__ = "income"
    income_id = Column(Integer, primary_key=True, autoincrement=True)
    year_month = Column(CHAR(7))
    monthly_income = Column(Float(4, 1))
    bonus = Column(Float(3, 1))
    username = Column(VARCHAR(16), ForeignKey("user.username"))
    __table_args__ = (UniqueConstraint(year_month, username),)

    user = relationship('User', back_populates='income')


class Todo(Base):
    __tablename__ = "todo"
    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(VARCHAR(32), nullable=False)
    status = Column(Boolean, default=False)
    username = Column(VARCHAR(16), ForeignKey("user.username"), nullable=False)
    __table_args__ = (UniqueConstraint(action, username),)

    user = relationship('User', back_populates='todo')


class User(Base):
    __tablename__ = "user"
    username = Column(VARCHAR(16), primary_key=True)
    password = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(32), unique=True)
    role = Column(Enum("admin", "general"), default="general")

    income = relationship('Income', back_populates='user')
    todo = relationship('Todo', back_populates='user')
    activity = relationship('Activity', back_populates='user')
    token = relationship('Token', back_populates='user')


class Token(Base):
    __tablename__ = "token"
    username = Column(VARCHAR(16), ForeignKey(
        "user.username"), primary_key=True)
    token = Column(VARCHAR(256))
    expires_at = Column(Date, nullable=False)
    status = Column(Boolean, default=True)

    user = relationship('User', back_populates='token')


class Inquiry(Base):
    __tablename__ = "inquiry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum("要望", "エラー報告", "その他"), nullable=False)
    detail = Column(VARCHAR(256), nullable=False)
    date = Column(Date, nullable=False)
    priority = Column(Enum("高", "中", "低"), default="低")
    is_checked = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
