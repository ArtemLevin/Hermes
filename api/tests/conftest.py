# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.deps import sync_engine, SyncSessionLocal
from api.models import Base
from api.security import hash_password
from api.models import User

@pytest.fixture(scope="function")
def client():
    # Create a new database for each test function
    Base.metadata.create_all(bind=sync_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=sync_engine)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": hash_password("password123"),
        "role": "tutor"
    }

@pytest.fixture
def auth_headers(client, test_user):
    # Create user
    client.post("/auth/register", json=test_user)
    # Login to get token
    response = client.post("/auth/token", data={"username": test_user["email"], "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}