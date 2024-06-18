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

engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
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

    # FastAPIの依存関係をオーバーライド
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # テスト終了後に依存関係のオーバーライドをリセット
    app.dependency_overrides[get_db] = get_db
