import pytest
from app.models import User
from app.auth import pwd_context
from sqlmodel import select

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Recipe Platform API"}

def test_create_user(client, test_db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    print(response.text)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data  # Check id is present
    assert "password" not in data  # Password shouldn’t be returned
    db_user = test_db.exec(select(User).where(User.username == "testuser")).first()
    assert pwd_context.verify("password123", db_user.hashed_password)