from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from app.models import User, UserCreate, UserResponse
from app.auth import create_access_token, pwd_context, get_current_user
from app.database import get_session
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone as dt_timezone

router = APIRouter()

class LoginRequest(BaseModel):
    """Defines login request data"""
    username: str
    password: str

@router.post("/token")
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Handles user login and returns access token."""
    # No username or password
    if not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    user = session.exec(select(User).where(User.username == request.username)).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Token expires after 1 hour
    token = create_access_token({"sub": user.username}, timedelta(hours=1))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """Creates a new user in database."""
    db_user = User(username=user.username, email=user.email, hashed_password=pwd_context.hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user) # Reload the user to add auto-generated fields
    return db_user  # Automatically maps to UserResponse

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Returns the current authenticated user's details."""
    return current_user