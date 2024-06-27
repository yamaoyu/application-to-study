from sqlalchemy import (Column, Integer, Float, Date,
                        Boolean, CHAR, VARCHAR)
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
    year_month = Column(CHAR(7), unique=True)
    monthly_income = Column(Float(4, 1))
    bonus = Column(Float(3, 1))


class Todo(Base):
    __tablename__ = "todo"
    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(VARCHAR(32))
    status = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
