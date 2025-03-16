from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import User, Recipe, Rating, Favorite
from typing import Optional, List
from datetime import datetime

app = FastAPI()

# using SQLite for now, echo=True for debugging
DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session

# Create tables on app run
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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
    author_id: int

class RecipeRead(Recipe):
    """Response model including auto-generated fields for id & created_at"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None

@app.post("/recipes/", response_model=RecipeRead)
async def create_recipe(recipe: RecipeCreate, session: Session = Depends(get_session)):
    db_recipe = Recipe(**recipe.dict())
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe

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
        raise HTTPException(staus_code=400, detail="Already favorited")
    db_favorite = Favorite(**favorite.dict())
    session.add(db_favorite)
    session.commit()
    session.refresh(db_favorite)
    return db_favorite
