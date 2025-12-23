import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{
    MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
