from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.models import User, Rating, Recipe, RecipeRead, RecipeCreate
from app.database import get_session
from app.auth import get_current_user
from typing import List
import json
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=RecipeRead)
async def create_recipe(recipe: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Recipe creation for current user."""
    logger.info(f"Creating recipe for user: {current_user.username}, ID: {current_user.id}")
    try:
        # Convert tags list to JSON string
        recipe_dict = recipe.model_dump()
         # Convert List[str] to str, in the actual frontend it's all strings now
        recipe_dict["tags"] = json.dumps(recipe_dict["tags"]) 
        recipe_dict["instructions"] = json.dumps(recipe_dict["instructions"]) 
        recipe_dict["author_id"] = current_user.id
        db_recipe = Recipe(**recipe_dict)
        session.add(db_recipe)
        session.commit()
        session.refresh(db_recipe)
        logger.info(f"Recipe created: {db_recipe.id}")
        return db_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")
    
@router.get("/", response_model=List[RecipeRead])
async def get_recipes(session: Session = Depends(get_session)):
    """Retrieve all recipes from database."""
    statement = select(Recipe) # SQLModel select to query all recipes
    recipes = session.exec(statement).all()
    return recipes # Return as list for RecipeRead format

# Get a specific recipe
@router.get("/{id}", response_model=RecipeRead)
async def get_recipe(id: int, session: Session = Depends(get_session)):
    recipe = session.get(Recipe,id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/recipes/{id}", response_model=RecipeRead)
async def update_recipe(id: int, recipe: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Update a recipe."""
    pass

@router.delete("/recipes/{id}", response_model=dict)
async def delete_recipe(id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Delete a recipe from database."""
    pass
    
@router.get("/{id}/average-rating", response_model=dict)
async def get_average_rating(id: int, session: Session = Depends(get_session)):
    """Get the average rating for a specific recipe."""
    # Check if recipe exists
    recipe = session.get(Recipe, id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    avg_rating = session.exec(
        select(func.avg(Rating.value)).where(Rating.recipe_id == id)
    ).first()

    if avg_rating is None:
        return {"average_rating": 0.0}
    
    return {"average_rating": round(float(avg_rating), 1)}