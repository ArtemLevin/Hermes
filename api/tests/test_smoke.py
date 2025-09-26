# tests/test_smoke.py
import pytest

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_register(client, test_user):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["role"] == test_user["role"]

def test_auth_login(client, test_user):
    # Register first
    client.post("/auth/register", json=test_user)
    # Login
    response = client.post("/auth/token", data={"username": test_user["email"], "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_students_unauthorized(client):
    response = client.get("/students/")
    assert response.status_code == 401

def test_get_students_authorized(client, auth_headers):
    response = client.get("/students/", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json() # Assuming the endpoint returns a list under 'items'