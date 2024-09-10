import os
from dotenv import load_dotenv
from backend.lib.security import get_password_hash
from db.database import SessionLocal
from db import db_model

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
APP_ADMIN_USER = os.getenv("APP_ADMIN_USER")
APP_ADMIN_PASSWORD = os.getenv("APP_ADMIN_PASSWORD")

hashed_password = get_password_hash(APP_ADMIN_PASSWORD)

db = SessionLocal()

try:
    # adminの登録確認
    fetch_admin = db.query(db_model.User).filter(
        db_model.User.username == APP_ADMIN_USER).one_or_none()

    if not fetch_admin:
        admin_data = db_model.User(
            username=APP_ADMIN_USER, password=hashed_password, role="admin")
        db.add(admin_data)
        db.commit()
        db.refresh(admin_data)

finally:
    db.close()
