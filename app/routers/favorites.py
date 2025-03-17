from app.auth import get_current_user
from app.database import get_session
from app.models import Favorite, FavoriteCreate, FavoriteRead, Recipe, User
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=FavoriteRead)
async def create_favorite(favorite: FavoriteCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Adds a recipe to a user's favorites."""
    # Check if recipe and user exist
    recipe = session.get(Recipe, favorite.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    # Check if already favorited
    existing = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id, 
            Favorite.recipe_id == favorite.recipe_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already favorited")
    db_favorite = Favorite(recipe_id=favorite.recipe_id, user_id=current_user.id)
    session.add(db_favorite)
    session.commit()
    session.refresh(db_favorite)
    return db_favorite

@router.get("/", response_model=FavoriteRead)
async def read_favorite(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Retrieve a user's rating for a recipe."""
    db_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id
        )
    ).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return db_favorite

@router.delete("/", response_model=dict)
async def remove_favorite(favorite: FavoriteCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Removes a recipe from user favorites."""
    # Check if favorite exists
    db_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == favorite.recipe_id
        )
    ).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Delete Favorite
    session.delete(db_favorite)
    session.commit()
    logger.info(f"Removed favorite: user_id={current_user.id}, recipe_id={favorite.recipe_id}")
    return {"message": f"Favorite (user_id={current_user.id}, recipe_id={favorite.recipe_id}) removed successfully"}