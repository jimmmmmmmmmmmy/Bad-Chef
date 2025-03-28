import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user(client, username="testuser", email="test@example.com", password="password123"):
    """Create a user and return the response."""
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = client.post("/users/", json=user_data)
    logger.info(f"Created user {username}: {response.text}")
    return response

def login_user(client, username="testuser", password="password123"):
    """Log in a user and return auth token."""
    login_data = {
        "username": username,
        "password": password
    }
    response = client.post("/users/token", json=login_data)
    logger.info(f"Login for {username}: {response.text}")
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]

def create_recipe(client, token, title="Test Recipe", description="test", \
    ingredients="Stuff", instructions=["Cook"], category="category", \
    image_source="http://example.com/test.jpg", serves=1, time="30 Min", \
    tags=['Spicy', 'Ramen']):
    """Create a recipe with given token and return the response."""
    recipe_data = {
        "title": title,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": category,
        "image_source": image_source,
        "serves": serves,
        "time": time,
        "tags": tags
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/recipes/", json=recipe_data, headers=headers)
    logger.info(f"Created recipe {title}: {response.text}")
    return response

def create_rating(client, recipe_id, token, value=3):
    rating_data = {
        "recipe_id": recipe_id,
        "value": value
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/ratings/", json=rating_data, headers=headers)
    logger.info(f"Rating response: {response.text}")
    return response