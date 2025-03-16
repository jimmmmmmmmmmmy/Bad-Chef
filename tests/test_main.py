from app.models import User
from app.auth import pwd_context
from sqlmodel import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Recipe Platform API"}

def test_create_user(client, test_db):
    """Test for creating user."""
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
    """Test for logging in with good credentials."""
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
    logger.info(f"Login response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_bad_login_1(client, test_db):
    """Test for login with valid username, bad password"""
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

def test_bad_login_2(client, test_db):
    """Test for login with invalid username"""
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

def test_create_recipe(client, test_db):
    """Test for creating recipe"""
    # Create user and login
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()["access_token"]

    # Create a recipe with user auth
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
        }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/recipes/", json=recipe_data, headers=headers)
    print(response.text)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Recipe"
    assert "id" in data
    assert data["author_id"] == 1

def test_get_recipes_1(client, test_db):
    """Test retrieving empty recipe db."""
    response = client.get("/recipes")
    logger.info(f"Empty recipes response: {response.text}")
    assert response.status_code == 200
    assert response.json() == []

def test_get_recipes_2(client, test_db):
    """Test post & get recipe."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()["access_token"]

    # Create a recipe with user auth
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
        }
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/recipes/", json=recipe_data, headers=headers)

    response=client.get("/recipes/")
    logger.info(f"Recipes response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Recipe"
    assert data[0]["author_id"] == 1

def test_get_recipes_3(client, test_db):
    """Test post & get recipe from two users."""
    # User 1
    user1_data = {
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user1_data)
    login_data1 = {
        "username": "testuser1",
        "password": "password123"
    }
    token_response1 = client.post("/token", json=login_data1)
    token1 = token_response1.json()["access_token"]
    # Create a recipe with user auth
    recipe_data1 = {
        "title": "Test Recipe 1",
        "description": "Test 1",
        "ingredients": "Stuff 1",
        "instructions": "Cook 1"
        }
    headers1 = {"Authorization": f"Bearer {token1}"}
    client.post("/recipes/", json=recipe_data1, headers=headers1)

    user2_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user2_data)

    login_data2 = {
        "username": "testuser2",
        "password": "password123"
    }
    token_response2 = client.post("/token", json=login_data2)
    token2 = token_response2.json()["access_token"]

    # Create a 2nd recipe with user auth
    recipe_data2 = {
        "title": "Test Recipe 2",
        "description": "Test 2",
        "ingredients": "Stuff 2",
        "instructions": "Cook 2"
        }
    headers2 = {"Authorization": f"Bearer {token2}"}
    client.post("/recipes/", json=recipe_data2, headers=headers2)

    response=client.get("/recipes/")
    logger.info(f"Recipes response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Recipe 1"
    assert data[0]["author_id"] == 1
    assert data[1]["title"] == "Test Recipe 2"
    assert data[1]["author_id"] == 2
    
def test_create_rating(client, test_db):
    """Test for valid rating."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()['access_token']
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
    }
    headers = {"Authorization": f"Bearer {token}"}
    recipe_response = client.post("/recipes/", json=recipe_data, headers=headers)
    recipe_id = recipe_response.json()["id"]

    rating_data = {
        "recipe_id": recipe_id,
        "user_id": 1,
        "value": 3
    }
    response = client.post("/ratings/", json=rating_data)
    logger.info(f"Rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 3
    assert data["recipe_id"] == recipe_id
    assert data["user_id"] == 1
    
def test_create_rating_2(client, test_db):
    """Test for invalid rating."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()['access_token']
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
    }
    headers = {"Authorization": f"Bearer {token}"}
    recipe_response = client.post("/recipes/", json=recipe_data, headers=headers)
    recipe_id = recipe_response.json()["id"]
    rating_data = {
        "recipe_id": recipe_id,
        "user_id": 1,
        "value": 4
    }
    response = client.post("/ratings/", json=rating_data)
    logger.info(f"Invalid response: {response.text}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Rating must be between 1 and 3"

def test_create_favorite(client, test_db):
    """Test adding a recipe to favorites."""
    user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()["access_token"]
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
    }
    headers = {"Authorization": f"Bearer {token}"}
    recipe_response = client.post("/recipes/", json=recipe_data, headers=headers)
    recipe_id = recipe_response.json()["id"]

    favorite_data = {
        "user_id": 1,
        "recipe_id": recipe_id
    }
    response = client.post("/favorites/", json=favorite_data)
    logger.info(f"Favorite response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["recipe_id"] == recipe_id
    assert "id" in data

def test_duplicate_favorite(client, test_db):
    """Test adding a favorite recipe twice."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    login_data = {"username": "testuser", "password": "password123"}
    token_response = client.post("/token", json=login_data)
    token = token_response.json()["access_token"]
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
    }
    headers = {"Authorization": f"Bearer {token}"}
    recipe_response = client.post("/recipes/", json=recipe_data, headers=headers)
    recipe_id = recipe_response.json()["id"]
    favorite_data = {"user_id": 1, "recipe_id": recipe_id}
    response = client.post("/favorites/", json=favorite_data)
    logger.info(f"Favorite response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["recipe_id"] == recipe_id
    assert "id" in data

    # Test duplicate favorite
    response = client.post("/favorites/", json=favorite_data)
    logger.info(f"Duplicate favorite response: {response.text}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Already favorited"

def test_remove_favorite(client, test_db):
    """Test adding a recipe to favorites."""
    user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    client.post("/users/", json=user_data)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    token_response = client.post("/token", json=login_data)
    token = token_response.json()["access_token"]
    recipe_data = {
        "title": "Test Recipe",
        "description": "Test",
        "ingredients": "Stuff",
        "instructions": "Cook"
    }
    headers = {"Authorization": f"Bearer {token}"}
    recipe_response = client.post("/recipes/", json=recipe_data, headers=headers)
    recipe_id = recipe_response.json()["id"]

    favorite_data = {
        "user_id": 1,
        "recipe_id": recipe_id
    }
    client.post("/favorites/", json=favorite_data)
    response = client.request('DELETE', '/favorites/', json=favorite_data)
    logger.info(f"Remove favorite response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Favorite (user_id=1, recipe_id={recipe_id}) removed successfully"
