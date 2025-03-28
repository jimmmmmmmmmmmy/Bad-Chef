import json
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine import Engine
from app.models import Recipe
from random import randint
import logging

# using SQLite for now, echo=True for debugging
DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(DATABASE_URL, echo=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_db_and_tables(db_engine: Engine = engine):
    """Creates all DB tables defined in models and seeds initial data if empty."""
    SQLModel.metadata.create_all(db_engine)
    with Session(db_engine) as session:
        # Check if the recipes table is empty
        recipe_count = session.exec(select(Recipe)).all()
        if not recipe_count:  # If empty, seed data
            # Load the JSON file
            # with open("./data/recipeData.json", "r") as file:
            with open("./data/frenchcookingacademy.json", "r") as file:
                recipes_data = json.load(file)
            
            # Add this for other Ollama parsed JSON files
            recipe_list = recipes_data["recipes"]

            # Insert each recipe from the JSON file
            for recipe_entry in recipe_list:
                # Map JSON fields to Recipe model
                recipe_data = recipe_entry["recipe"] 
                # Convert ingredients list to a string
                ingredients_str = ", ".join(
                    f"{ing['amount']} {ing['unit']} {ing['id']}"+"\n" 
                    for ing in recipe_data["ingredients"]
                )
                # Serialize Python objects into strong w/ JSON syntax
                tags_json = json.dumps(recipe_data.get("tags", []))
                instructions_json = json.dumps(recipe_data.get("instructions", []))
                
                sample_recipe = Recipe(
                    title=recipe_data["title"],
                    description=recipe_data["description"],
                    ingredients=ingredients_str,
                    instructions=instructions_json,
                    author_id=randint(1, 10),
                    category=recipe_data.get("category", ""),
                    image_source=recipe_data["image_source"],
                    serves=recipe_data["serves"],
                    time=recipe_data["time"],
                    tags=tags_json
                )
                session.add(sample_recipe)
            
            session.commit()
            print(f"Seeded database with {len(recipes_data)} recipes from recipeData.json.")

def get_session():
    """Yields a database session for FastAPI."""
    with Session(engine) as session:
        yield session