from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine

# using SQLite for now, echo=True for debugging
DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables(db_engine: Engine = engine):
    SQLModel.metadata.create_all(db_engine)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session