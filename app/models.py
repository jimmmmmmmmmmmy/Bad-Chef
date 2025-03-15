from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str 
    ingredients: str # Potentially use JSON later
    instructions: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Rating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key = True)
    recipe_id: int = Field(foreign_key="recipe.id")
    user_id: int = Field(foreign_key="user.id")
    value: int = Field(ge=1, le=5) # 1 to 5 rating

class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    recipe_id: int = Field(foreign_key="recipe.id")