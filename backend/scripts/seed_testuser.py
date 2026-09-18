"""アプリ起動時にテスト用の一般ユーザーを作成するモジュール。

フロントエンドのe2eテストではユーザーがログインし、ページリロードしてもログイン状態を維持できることを検証している。
この検証をするにはモックでは対応できないため、予め一般ユーザーを作成しておく
"""

import os
from app.security.password import get_password_hash
from db.database import SessionLocal
from db import db_model

BASE_URL = os.getenv("BASE_URL")
E2E_TEST_USER = os.getenv("E2E_TEST_USER")
E2E_TEST_PASSWORD = os.getenv("E2E_TEST_PASSWORD")

hashed_password = get_password_hash(E2E_TEST_PASSWORD)

db = SessionLocal()

try:
    fetch_user = db.query(db_model.User).filter(
        db_model.User.username == E2E_TEST_USER).one_or_none()

    if not fetch_user:
        user_data = db_model.User(
            username=E2E_TEST_USER, password=hashed_password, role="general")
        db.add(user_data)
        db.commit()
        db.refresh(user_data)
    print(f"{E2E_TEST_USER}を作成")
except Exception as e:
    print(f"Error occurred: {e}")
    db.rollback()
finally:
    db.close()
