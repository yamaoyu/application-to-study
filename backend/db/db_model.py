from sqlalchemy import Column, Integer, Float, Date, Boolean, CHAR
from db.database import Base, engine


class Activity(Base):
    __tablename__ = "activity"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True)
    target = Column(Float(3, 1))
    study = Column(Float(3, 1))
    is_achieved = Column(Boolean)


class Salary(Base):
    __tablename__ = "salary"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    year_month = Column(CHAR(7), unique=True)
    monthly_income = Column(Integer)
    bonus = Column(Integer)
    add_monthly_income = Column(Integer)


Base.metadata.create_all(bind=engine)
