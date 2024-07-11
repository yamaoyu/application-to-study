from sqlalchemy import (Column, Integer, Float, Date, Boolean,
                        CHAR, VARCHAR, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from db.database import Base, engine


class Activity(Base):
    __tablename__ = "activity"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True)
    target = Column(Float(3, 1))
    actual = Column(Float(3, 1))
    is_achieved = Column(Boolean)


class Income(Base):
    __tablename__ = "income"
    income_id = Column(Integer, primary_key=True, autoincrement=True)
    year_month = Column(CHAR(7))
    monthly_income = Column(Float(4, 1))
    bonus = Column(Float(3, 1))
    username = Column(VARCHAR(16), ForeignKey("user.username"))
    UniqueConstraint(year_month, username)

    user = relationship('User', back_populates='income')


class Todo(Base):
    __tablename__ = "todo"
    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(VARCHAR(32), nullable=False)
    status = Column(Boolean, default=False)
    username = Column(VARCHAR(16), ForeignKey("user.username"), nullable=False)
    UniqueConstraint(action, username)

    user = relationship('User', back_populates='todo')


class User(Base):
    __tablename__ = "user"
    username = Column(VARCHAR(16), primary_key=True)
    password = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(32), default=None)

    income = relationship('Income', back_populates='user')
    todo = relationship('Todo', back_populates='user')


Base.metadata.create_all(bind=engine)
