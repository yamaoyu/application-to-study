from sqlalchemy import Column, Integer, Float, Date, Boolean
from db.database import Base, engine


class Activity(Base):
    __tablename__ = "activity"
    date = Column(Date, primary_key=True)
    target = Column(Float(3, 1))
    study = Column(Float(3, 1))
    is_achieved = Column(Boolean)


class Salary(Base):
    __tablename__ = "salary"
    month = Column(Date, primary_key=True)
    monthly_income = Column(Integer)
    bonus = Column(Integer)
    add_monthly_income = Column(Integer)


Base.metadata.create_all(bind=engine)
