from app.models import User
from app.auth import pwd_context
from sqlmodel import select
from tests.test_utils import create_user, login_user, create_recipe, create_rating
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Recipe Platform API"}

def test_create_user(client, test_db):
    """Test for creating user."""
    response = create_user(client)
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
    create_user(client)
    token = login_user(client)
    assert "eyJ" in token  # Basic JWT check

def test_bad_login_1(client, test_db):
    """Test for login with valid username, bad password."""
    create_user(client)
    response = client.post("/users/token", json={"username": "testuser", "password": "password"})
    logger.info(f"Bad password response: {response.text}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_bad_login_2(client, test_db):
    """Test for login with invalid username."""
    create_user(client)
    response = client.post("/users/token", json={"username": "testuser123", "password": "password123"})
    logger.info(f"Bad username response: {response.text}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_create_recipe(client, test_db):
    """Test for creating recipe"""
    create_user(client)
    token = login_user(client)
    response = create_recipe(client, token)
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
    create_user(client)
    token = login_user(client)
    create_recipe(client, token)
    response=client.get("/recipes/")
    logger.info(f"Recipes response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Recipe"
    assert data[0]["author_id"] == 1

def test_get_recipes_3(client, test_db):
    """Test post & get recipe from two users."""
    # Create user 1
    create_user(client, "testuser1", "test1@example.com")
    token1 = login_user(client, "testuser1")
    create_recipe(client, token1, "Test Recipe 1", "Test 1", "Stuff 1", "Cook 1")
    # Create user 2
    create_user(client, "testuser2", "test2@example.com")
    token2 = login_user(client, "testuser2")
    create_recipe(client, token2, "Test Recipe 2", "Test 2", "Stuff 2", "Cook 2")
    # Check if both recipes have been added and properly attributed
    response=client.get("/recipes/")
    logger.info(f"Recipes response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Recipe 1"
    assert data[0]["author_id"] == 1
    assert data[1]["title"] == "Test Recipe 2"
    assert data[1]["author_id"] == 2

def test_get_specific_recipe(client, test_db):
    """Get a recipe, specifically."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    # Fetch create recipe
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id
    assert data["title"] == "Test Recipe"
    assert data["description"] == "test"
    assert data["ingredients"] == "Stuff"
    assert data["instructions"] == "Cook"

def test_remove_recipe(client, test_db):
    """Not implemented for now."""
    pass

def test_get_average_rating(client, test_db):
    """Test getting the average rating for a recipe."""
    # Create user 1 and a recipe
    create_user(client, "user1", "user1@example.com")
    token1 = login_user(client, "user1")
    recipe_response = create_recipe(client, token1)
    recipe_id = recipe_response.json()["id"]

    # User 1 rates the recipe (value=3)
    create_rating(client, recipe_id, token1, value=3)

    # Create user 2 and rate the same recipe (value=2)
    create_user(client, "user2", "user2@example.com")
    token2 = login_user(client, "user2")
    create_rating(client, recipe_id, token2, value=2)

    # Get average rating
    response = client.get(f"/recipes/{recipe_id}/average-rating")
    logger.info(f"Average rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 2.5
    
def test_create_rating(client, test_db):
    """Test for valid rating."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    response = create_rating(client, recipe_id, token)
    logger.info(f"Rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    # Check if rating has been attributed correctly to recipe
    assert data["value"] == 3
    assert data["recipe_id"] == recipe_id
    assert data["user_id"] == 1
    
def test_create_rating_2(client, test_db):
    """Test for invalid rating."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    response = client.post("/ratings/", json={"recipe_id": recipe_id, "user_id": 1, "value": 6}, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Invalid response: {response.text}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Rating must be between 1 and 3"

def test_read_reating(client, test_db):
    """Test reading/retrieving a rating for a recipe."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)

    response = client.get(f"/ratings/?user_id=1&recipe_id={recipe_id}", headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Read rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["recipe_id"] == recipe_id
    assert data["value"] == 3

def test_read_rating_2(client, test_db):
    """Test non-authenticated rating retrieval."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)
    # Get a rating from valid recipe / invalid user id
    response = client.get(f"/ratings/?user_id=2&recipe_id={recipe_id}", )
    logger.info(f"Read non-existent rating response: {response.text}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"

def test_update_rating(client, test_db):
    """Test for update rating."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)
    # Update rating from 3 to 1
    rating_data = {
        "recipe_id": recipe_id,
        "value": 1
    }
    response = client.put("/ratings/", json=rating_data, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Update rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["value"] == 1

def test_update_rating_1(client, test_db):
    """Test update with invalid rating."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)
    # Update rating from 3 to 10
    rating_data = {
        "recipe_id": recipe_id,
        "value": 10
    }
    response = client.put("/ratings/", json=rating_data, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Update invalid rating response: {response.text}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Rating must be between 1 and 3"

def test_update_rating_2(client, test_db):
    """Test updating a rating that doesn’t exist for the authenticated user."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)

    create_user(client, "user2", "user2@example.com")
    token2 = login_user(client, "user2")
    # Update rating using 2nd users credentials
    rating_data = {
        "recipe_id": recipe_id,
        "value": 3
    }
    response = client.put("/ratings/", json=rating_data, headers={"Authorization": f"Bearer {token2}"})
    logger.info(f"Update non-existent rating response: {response.text}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Rating not found"

def test_remove_rating(client, test_db):
    """Test for remove user rating."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    create_rating(client, recipe_id, token)
    # Delete the recent user data
    rating_data = {"recipe_id": recipe_id, "value": 3}
    response = client.request('DELETE', '/ratings/', json=rating_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Rating (user_id=1, recipe_id={recipe_id}) removed successfully"

def test_create_favorite(client, test_db):
    """Test adding a recipe to favorites."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    # Add recipe_id to user favorites
    favorite_data = {
        "recipe_id": recipe_id
    }
    response = client.post("/favorites/", json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Favorite response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["user_id"] == 1

def test_read_favorite(client, test_db):
    """Test reading/retrieving a favorite."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    # Add recipe_id to user favorites
    favorite_data = {
        "recipe_id": recipe_id
    }
    client.post("/favorites/", json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    response = client.get(f"/favorites/?recipe_id={recipe_id}", headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Read rating response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["user_id"] == 1

def test_read_favorite_2(client, test_db):
    """Test retrieving a non-existent user but valid recipe."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    # Add recipe_id to user favorites
    favorite_data = {
        "user_id": 2,
        "recipe_id": recipe_id
    }
    client.post("/favorites/", json=favorite_data)
    response = client.get(f"/favorites/?recipe_id={recipe_id}", headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Read rating response: {response.text}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Favorite not found"

def test_duplicate_favorite(client, test_db):
    """Test adding a favorite recipe twice."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    # Added favorite the first time
    favorite_data = {"user_id": 1, "recipe_id": recipe_id}
    response = client.post("/favorites/", json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    # Test duplicate favorite
    response = client.post("/favorites/", json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Duplicate favorite response: {response.text}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Already favorited"

def test_remove_favorite(client, test_db):
    """Test removing a recipe from favorites."""
    create_user(client)
    token = login_user(client)
    recipe_response = create_recipe(client, token)
    recipe_id = recipe_response.json()["id"]
    favorite_data = {
        "recipe_id": recipe_id
    }
    client.post("/favorites/", json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    # client.request with a 'DELETE' in there, as there's no client.delete()
    response = client.request('DELETE', '/favorites/', json=favorite_data, headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Remove favorite response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Favorite (user_id=1, recipe_id={recipe_id}) removed successfully"
