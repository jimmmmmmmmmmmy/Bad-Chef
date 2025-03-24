from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import datetime as dt

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str

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

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str 
    ingredients: str # Potentially use JSON later
    instructions: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(dt.UTC))
    imageSource: str
    category: str

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

class Rating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key = True)
    recipe_id: int = Field(foreign_key="recipe.id")
    user_id: int = Field(foreign_key="user.id")
    value: int = Field(ge=1, le=3) # 1 to 3 rating

class RatingCreate(SQLModel):
    """Structure for creating a recipe rating."""
    recipe_id: int
    value: int

class RatingRead(Rating):
    """Response model for reading rating data."""
    pass

class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    recipe_id: int = Field(foreign_key="recipe.id")
    
class FavoriteCreate(SQLModel):
    recipe_id: int  # Only what's sent in the request

class FavoriteRead(Favorite):
    pass

class FavoriteReadDetailed(Favorite):
    id: int
    recipe_id: int
    title: str
    author_id: int
    category: str # LOOOOOL forgot to pass this to frontend LMAOOOO
    imageSource: str