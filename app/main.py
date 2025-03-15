from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel, Session
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcoem to the Recipe Platform API"}

# using SQLite for now, echo=True for debugging
DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Create tables on app run
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe Platform API"}