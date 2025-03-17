import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.main import app as fastapi_app
from app.database import get_session

@pytest.fixture(scope="function")
def test_engine():
    db_path = "test.db"
    # Clean slate for each test run
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine("sqlite:///test.db", echo=False) # True if log SQL statements
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created.")
    yield engine
    # Clean up schema after test
    SQLModel.metadata.drop_all(engine)
    # Delete test.db
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(scope="function")
def test_db(test_engine):
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_db):
    def _override_get_session():
        yield test_db
    fastapi_app.dependency_overrides[get_session] = _override_get_session
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()