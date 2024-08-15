import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from app.main import app
from dotenv import load_dotenv

load_dotenv()


MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
TEST_MYSQL_DATABASE = os.getenv("TEST_MYSQL_DATABASE")
TEST_DATABASE_URL = f"mysql+pymysql://root:{
    MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}/{TEST_MYSQL_DATABASE}"
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "ecd518ef9af267a68cd92ae2ba3e8570eae25c713a84dedf0b96066e7d73d205"
)
ALGORITHM = os.getenv("ALGORITHM", "HS256")

engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
        finally:
            db_session.close()

    # FastAPIの依存関係をオーバーライド(本番用のDBに接続しないようにするため)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # テスト終了後に依存関係のオーバーライドをリセット
    del app.dependency_overrides[get_db]


test_username = "testuser"
test_plain_password = "password"


@pytest.fixture(scope="function", autouse=True)
def create_user(client):
    """ 基本的にはここで作成するユーザーを使用 """
    data = {"username": test_username,
            "password": test_plain_password,
            "email": "test@test.com"}
    user = client.post("/register", json=data)
    return user


@pytest.fixture(scope="function", autouse=True)
def login_and_get_token(client):
    data = {"username": test_username, "password": test_plain_password}
    token = client.post("/login", json=data)
    return token


@pytest.fixture(scope="function", autouse=True)
def get_headers(login_and_get_token):
    access_token = login_and_get_token.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
