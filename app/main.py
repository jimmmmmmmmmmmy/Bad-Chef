from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables, engine
from app.routers.users import router as users_router
from app.routers.ratings import router as ratings_router
from app.routers.recipes import router as recipes_router
from app.routers.favorites import router as favorites_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application lifespan by creating DB tables on startup."""
    create_db_and_tables(engine) # Create DB schema before app starts
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Welcome messgae for API root endpoint."""
    return {"message": "Welcome to the Recipe Platform API"}

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
app.include_router(ratings_router, prefix="/ratings", tags=["ratings"])
app.include_router(favorites_router, prefix="/favorites", tags=["favorites"])