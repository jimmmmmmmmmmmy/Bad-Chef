from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session, SQLModel
from app.models import User, Recipe, Rating, Favorite
from app.auth import create_access_token, get_current_user, pwd_context
from app.database import get_session, create_db_and_tables, engine
from pydantic import BaseModel
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application lifespan by creating DB tables on startup."""
    create_db_and_tables(engine) # Create DB schema before app starts
    yield

app = FastAPI(lifespan=lifespan)

# Login Endpoint
class LoginRequest(BaseModel):
    """Defines login request data"""
    username: str
    password: str

@app.post("/token")
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Handles user login and returns access token."""
    user = session.exec(select(User).where(User.username == request.username)).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
async def root():
    """Welcome messgae for API root endpoint."""
    return {"message": "Welcome to the Recipe Platform API"}

class UserCreate(SQLModel):
    """Structure for creating a new user."""
    username: str
    email: str
    password: str

class UserResponse(SQLModel):
    """Structure for user response data."""
    username: str
    email: str
    id: Optional[int] = None

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """Creates a new user in database."""
    db_user = User(username=user.username, email=user.email, hashed_password=pwd_context.hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user) # Reload the user to add auto-generated fields
    return db_user  # Automatically maps to UserResponse

class RecipeCreate(SQLModel):
    """Input model for creating a recipe."""
    title: str
    description: str
    ingredients: str
    instructions: str
    # Removed author_id as we're passing it in the post

class RecipeRead(Recipe):
    """Response model including auto-generated fields for id & created_at"""
    # Empty for now
    pass

@app.post("/recipes/", response_model=RecipeRead)
async def create_recipe(recipe: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Recipe creation for current user."""
    logger.info(f"Creating recipe for user: {current_user.username}, ID: {current_user.id}")
    try:
        # Unpack recipe data and add author
        db_recipe = Recipe(**recipe.model_dump(), author_id=current_user.id) 
        session.add(db_recipe)
        session.commit()
        # Refresh for auto-generated fields
        session.refresh(db_recipe)
        logger.info(f"Recipe created: {db_recipe.id}")
        return db_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")
    
# Recipe Browsing Endpoint
@app.get("/recipes/", response_model=List[RecipeRead])
async def get_recipes(session: Session = Depends(get_session)):
    """Retrieve all recipes from database."""
    statement = select(Recipe) # SQLModel select to query all recipes
    recipes = session.exec(statement).all()
    return recipes # Return as list for RecipeRead format

# Rating Creation Endpoint
class RatingCreate(SQLModel):
    """Structure for creating a recipe rating."""
    recipe_id: int
    user_id: int
    value: int

class RatingRead(Rating):
    """Response model for reading rating data."""
    pass

@app.post("/ratings/", response_model=RatingRead)
async def create_rating(rating: RatingCreate, session: Session = Depends(get_session)):
    """Creates a new rating for a recipe."""
    recipe = session.get(Recipe, rating.recipe_id) # Verify recipe exists
    user = session.get(User, rating.user_id) # Verify user exists
    if not recipe or not user:
        raise HTTPException(status_code=404, detail="Recipe or User not found")
    if rating.value < 1 or rating.value > 3:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 3")
    db_rating = Rating(**rating.model_dump())
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating

@app.get("/ratings/", response_model=RatingRead)
async def read_rating(user_id: int, recipe_id: int, session: Session = Depends(get_session)):
    """Retrieve a user's rating for a recipe."""
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.recipe_id == recipe_id
        )
    ).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@app.put("/ratings/", response_model=RatingRead)
async def update_rating(rating: RatingCreate, session: Session = Depends(get_session)):
    """Update a user's rating for a recipe."""
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == rating.user_id,
            Rating.recipe_id == rating.recipe_id
        )
    ).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.value < 1 or rating.value > 3:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 3")
    db_rating.value = rating.value
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    logging.info(f"Updated rating: user_id={rating.user_id}, recipe_id={rating.recipe_id}, value={rating.value}")
    return db_rating

@app.delete("/ratings/", response_model=dict)
async def remove_rating(rating: RatingCreate, session: Session = Depends(get_session)):
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == rating.user_id,
            Rating.recipe_id == rating.recipe_id
        )
    ).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    session.delete(db_rating)
    session.commit()
    logger.info(f"Removed rating: user_id={rating.user_id}, recipe_id={rating.recipe_id}")
    return {"message": f"Rating (user_id={rating.user_id}, recipe_id={rating.recipe_id}) removed successfully"}

# Favorite Creation Endpoint
class FavoriteCreate(SQLModel):
    """Structure for creating a favorite recipe entry."""
    user_id: int
    recipe_id: int

class FavoriteRead(Favorite):
    """Response model for reading favorite data."""
    pass

@app.post("/favorites/", response_model=FavoriteRead)
async def create_favorite(favorite: FavoriteCreate, session: Session = Depends(get_session)):
    """Adds a recipe to a user's favorites."""
    # Check if recipe and user exist
    recipe = session.get(Recipe, favorite.recipe_id)
    user = session.get(User, favorite.user_id)
    if not recipe or not user:
        raise HTTPException(status_code=404, detail="Recipe or User not found")
    # Check if already favorited
    existing = session.exec(select(Favorite).where(Favorite.user_id == favorite.user_id, Favorite.recipe_id == favorite.recipe_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already favorited")
    db_favorite = Favorite(**favorite.model_dump())
    session.add(db_favorite)
    session.commit()
    session.refresh(db_favorite)
    return db_favorite

@app.get("/favorites/", response_model=FavoriteRead)
async def read_favorite(user_id: int, recipe_id: int, session: Session = Depends(get_session)):
    """Retrieve a user's rating for a recipe."""
    db_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.recipe_id == recipe_id
        )
    ).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return db_favorite

@app.delete("/favorites/", response_model=dict)
async def remove_favorite(favorite: FavoriteCreate, session: Session = Depends(get_session)):
    """Removes a recipe from user favorites."""
    # Check if favorite exists
    db_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == favorite.user_id,
            Favorite.recipe_id == favorite.recipe_id
        )
    ).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Delete Favorite
    session.delete(db_favorite)
    session.commit()
    logger.info(f"Removed favorite: user_id={favorite.user_id}, recipe_id={favorite.recipe_id}")
    return {"message": f"Favorite (user_id={favorite.user_id}, recipe_id={favorite.recipe_id}) removed successfully"}