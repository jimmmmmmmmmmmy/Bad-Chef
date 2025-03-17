from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, create_db_and_tables
from app.users import router as users_router
from app.recipes import router as recipes_router
from app.ratings import router as ratings_router
from app.favorites import router as favorites_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe Platform API"}

# Include routers
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
app.include_router(ratings_router, prefix="/ratings", tags=["ratings"])
app.include_router(favorites_router, prefix="/favorites", tags=["favorites"])