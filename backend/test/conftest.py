import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from app.main import app
from testdata import (RESOURCE_OWNER_USERNAME, RESOURCE_OWNER_PLAIN_PASSWORD,
                      RESOURCE_OWNER_EMAIL, NON_RESOURCE_OWNER_USERNAME, NON_RESOURCE_OWNER_PLAIN_PASSWORD)


MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
TEST_MYSQL_DATABASE = os.getenv("TEST_MYSQL_DATABASE")
TEST_DATABASE_URL = f"mysql+pymysql://root:{
    MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}/{TEST_MYSQL_DATABASE}"
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSession = sessionmaker(autocommit=False, bind=engine)


@pytest.fixture(autouse=True, scope="function")
def create_test_table():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """テストクライアントを作成して提供するfixture"""

    # データベースセッションの依存関係をオーバーライド
    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()

    # FastAPIの依存関係をオーバーライド(本番用のDBに接続しないようにするため)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # テスト終了後に依存関係のオーバーライドをリセット
    del app.dependency_overrides[get_db]


@pytest.fixture()
def create_resource_owner(client):
    """ 基本的にはここで作成するユーザーを使用 """
    data = {"username": RESOURCE_OWNER_USERNAME,
            "password": RESOURCE_OWNER_PLAIN_PASSWORD,
            "email": RESOURCE_OWNER_EMAIL}
    user = client.post("/users", json=data)
    return user


@pytest.fixture()
def login_resource_owner(client, create_resource_owner):
    data = {"username": RESOURCE_OWNER_USERNAME, "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    token = client.post("/login", json=data)
    return token


@pytest.fixture()
def get_resource_owner_headers(login_resource_owner):
    access_token = login_resource_owner.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


@pytest.fixture()
def create_non_resource_owner(client):
    """ 他のユーザーが作成したデータにアクセスできないか確認するために使用 """
    data = {"username": NON_RESOURCE_OWNER_USERNAME,
            "password": NON_RESOURCE_OWNER_PLAIN_PASSWORD}
    user = client.post("/users", json=data)
    return user


@pytest.fixture()
def login_non_resource_owner(client, create_non_resource_owner):
    data = {"username": NON_RESOURCE_OWNER_USERNAME, "password": NON_RESOURCE_OWNER_PLAIN_PASSWORD}
    token = client.post("/login", json=data)
    return token


@pytest.fixture()
def get_non_resource_owner_headers(login_non_resource_owner):
    access_token = login_non_resource_owner.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
