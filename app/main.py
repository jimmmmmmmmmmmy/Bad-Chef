from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session, SQLModel
from app.models import User, Recipe, Rating, Favorite
from app.auth import create_access_token, get_current_user, pwd_context
from app.database import get_session, create_db_and_tables  # New import
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create tables on app run
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Login Endpoint
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == request.username)).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe Platform API"}

# User Creation Endpoint, Pydantic-style for input validation
class UserCreate(SQLModel):
    username: str
    email: str
    hashed_password: str

@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(**user.dict())
    db_user.hashed_password = pwd_context.hash(db_user.hashed_password) # Hash the password
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Recipe Recreation Endpoint
class RecipeCreate(SQLModel):
    """Input model for creating a recipe."""
    title: str
    description: str
    ingredients: str
    instructions: str
    # Removed author_id as we're passing it in the post

class RecipeRead(Recipe):
    """Response model including auto-generated fields for id & created_at"""
    pass

@app.post("/recipes/", response_model=RecipeRead)
async def create_recipe(recipe: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    logger.info(f"Creating recipe for user: {current_user.username}, ID: {current_user.id}")
    try:
        db_recipe = Recipe(**recipe.dict(), author_id=current_user.id)
        session.add(db_recipe)
        session.commit()
        session.refresh(db_recipe)
        logger.info(f"Recipe created: {db_recipe.id}")
        return db_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")
    
# Recipe Browsing Endpoint
@app.get("/recipes/", response_model=List[RecipeRead])
async def get_recipes(session: Session = Depends(get_session)):
    statement = select(Recipe) # SQLModel select to query all recipes
    recipes = session.exec(statement).all()
    return recipes # Return as list for RecipeRead format

# Rating Creation Endpoint
class RatingCreate(SQLModel):
    recipe_id: int
    user_id: int
    value: int

class RatingRead(Rating):
    id: Optional[int] = None

@app.post("/ratings/", response_model=RatingRead)
async def create_rating(rating: RatingCreate, session: Session = Depends(get_session)):
    # Check if recipe and user exist
    recipe = session.get(Recipe, rating.recipe_id)
    user = session.get(User, rating.user_id)
    if not recipe or not user:
        raise HTTPException(status_code=404, detail="Recipe or User not found")
    if rating.value < 1 or rating.value > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    db_rating = Rating(**rating.dict())
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating

# Favorite Creation Endpoint
class FavoriteCreate(SQLModel):
    user_id: int
    recipe_id: int

class FavoriteRead(Favorite):
    id: Optional[int] = None

@app.post("/favorites/", response_model=FavoriteRead)
async def create_favorite(favorite: FavoriteCreate, session: Session = Depends(get_session)):
    # Check if recipe and user exist
    recipe = session.get(Recipe, favorite.recipe_id)
    user = session.get(User, favorite.user_id)
    if not recipe or not user:
        raise HTTPException(status_code=404, detail="Recipe or User not found")
    # Check if already favorited
    existing = session.exec(select(Favorite).where(Favorite.user_id == favorite.user_id, Favorite.recipe_id == favorite.recipe_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already favorited")
    db_favorite = Favorite(**favorite.dict())
    session.add(db_favorite)
    session.commit()
    session.refresh(db_favorite)
    return db_favorite
