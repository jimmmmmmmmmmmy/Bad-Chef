from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import User, Recipe, Rating, RatingCreate, RatingRead
from app.auth import get_current_user
from app.database import get_session
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=RatingRead)
async def create_rating(rating: RatingCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Creates a new rating for a recipe."""
    recipe = session.get(Recipe, rating.recipe_id) # Verify recipe exists
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if rating.value < 1 or rating.value > 3:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 3")
    db_rating = Rating(recipe_id=rating.recipe_id, user_id=current_user.id, value=rating.value)
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating

@router.get("/", response_model=RatingRead)
async def read_rating(user_id: int, recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Retrieve a user's rating for a recipe."""
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.recipe_id == recipe_id
        )
    ).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@router.put("/", response_model=RatingRead)
async def update_rating(rating: RatingCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Update a user's rating for a recipe."""
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == current_user.id,
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
    logging.info(f"Updated rating: user_id={current_user.id}, recipe_id={rating.recipe_id}, value={rating.value}")
    return db_rating

@router.delete("/", response_model=dict)
async def remove_rating(rating: RatingCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_rating = session.exec(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.recipe_id == rating.recipe_id
        )
    ).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    session.delete(db_rating)
    session.commit()
    logger.info(f"Removed rating: user_id={current_user.id}, recipe_id={rating.recipe_id}")
    return {"message": f"Rating (user_id={current_user.id}, recipe_id={rating.recipe_id}) removed successfully"}
