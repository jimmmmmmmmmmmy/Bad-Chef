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

def test_good_login_user(client, test_db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)

    # Test successful login
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/token", json=login_data)
    print(response.text)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_bad_login_pw(client, test_db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)

    # Test successful login
    login_data = {
        "username": "testuser",
        "password": "password"
    }
    response = client.post("/token", json=login_data)
    print(response.text)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_bad_login_user(client, test_db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)

    # Test successful login
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    response = client.post("/token", json=login_data)
    print(response.text)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"