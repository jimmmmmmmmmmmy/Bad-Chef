import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from typing import Dict, Optional
import logging
import pdfplumber
from ollama import chat, ChatResponse
from pydantic import BaseModel
from typing import List
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.recipe_data = {}  # Changed to dict to match return type

    def fetch_page(self, url: str) -> Optional[str]:
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        logger.info(f"logged page {url}")
        return response.text
        
    def fetch_pdf(self, url: str):
        response = requests.get(url, headers=self.headers, timeout=10)
        logger.info(f"now scraping: {url}")
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text

    def find_print_url(self, html: str, base_url: str):
        """Find the print button on a recipe page."""
        soup = BeautifulSoup(html, 'html.parser')

        all_buttons = soup.find_all(['a', 'button'], recursive=True)
        for some_button in all_buttons:
            button_classes = some_button.get('class', [])
            for some_class in button_classes:
                if 'print' in some_class.lower() \
                    or 'print recipe' in some_class.lower() \
                    or 'wprm-recipe-print' in some_class.lower() \
                    or 'recipe-print' in some_class.lower():
                    href = some_button.get('href')
                    if href:
                        print_url = urljoin(base_url, href)
                        logger.info(f"Found printurl at {print_url}")
                        return print_url
            text = some_button.get_text(strip=True).lower()
            if 'print' in text:
                href = some_button.get('href')
                if href:
                    print_url = urljoin(base_url, href)
                    logger.info(f"printURL found at {print_url}")
                    return print_url
        logger.warning(f"no print url found on {base_url}")

    def scrape(self) -> Dict:
        main_html = self.fetch_page(self.url)
        print_url = self.find_print_url(main_html, self.url)
        if print_url.lower().endswith('.pdf'):
            raw_text = self.fetch_pdf(print_url)
        else:
            print_html = self.fetch_page(print_url)
            soup = BeautifulSoup(print_html, 'html.parser')
            raw_text = soup.get_text(separator="\n", strip=True)
        logger.info(f"{raw_text}")
        return raw_text #Print out the entire recipe

def scrape_recipe(url: str) -> Dict:
    scraper = RecipeScraper(url)
    return scraper.scrape()

class Ingredient(BaseModel):
    id: str
    amount: float
    unit: str

class Instructions(BaseModel):
    Steps: List[str]

class Recipe(BaseModel):
    title: str
    time: str
    serves: int
    creator: str
    ingredients: List[Ingredient]
    description: str
    instructions: Instructions
    image_source: str
    category: str
    tags: List[str]

class Response(BaseModel):
    agent_response: str
    recipe: Recipe

def ollama_parse(text: str, url: str):

    schema = """
    {
        "title": "Spaghetti and Meatballs",
        "time": "30 Mins",
        "serves": 2,
        "creator": "Italian Chef",
        "ingredients": [
            {"id": "spaghetti", "amount": 1, "unit": "lb"},
            {"id": "ground_beef", "amount": 1, "unit": "lb"},
            {"id": "breadcrumbs", "amount": 1, "unit": "cup"},
            {"id": "egg", "amount": 1, "unit": "piece"},
            {"id": "garlic", "amount": 2, "unit": "clove"},
            {"id": "tomato_sauce", "amount": 1, "unit": "can"},
            {"id": "oregano", "amount": 1, "unit": "tsp"},
            {"id": "salt", "amount": 1, "unit": "to taste"},
            {"id": "pepper", "amount": 1, "unit": "to taste"}
        ],
        "description": "Classic Italian comfort food with juicy meatballs and tangy tomato sauce.",
        "instructions": {
            "Steps": [
                "Cook spaghetti according to package instructions.",
                "Mix ground beef, breadcrumbs, egg, and garlic. Form into meatballs.",
                "Brown meatballs in a pan, then add tomato sauce and oregano.",
                "Simmer for 20 minutes.",
                "Serve meatballs and sauce over spaghetti."
            ]
        },
        "image_source": "../assets/spaghetti_meatballs.png",
        "category": "Dinner", 
        "tags": ["Italian", "pasta", "meat", "savory", "dinner", "juicy", "tangy", "classic"]
    }
    """

    response: ChatResponse = chat(
        model='llama3:latest',
        messages=[
            {
                'role': 'user',
                'content': f"""
                    Convert the following recipe text into a JSON object matching the schema below. Follow these rules strictly:
                    - Return a single, valid JSON object with exactly two top-level keys: "agent_response" (a string for commentary, e.g., estimation explanations) and "recipe" (containing the recipe data per the schema).
                    - Do not include any text, comments, or explanations outside the JSON object.
                    - For "ingredients", extract "id" (ingredient name), "amount" (numeric value), and "unit" (string) from each line.
                    - Set "creator" by inferring from the URL
                    - If "time" or "serves" is unspecified, estimate (e.g., "30 Mins" for time, 4 for serves).
                    - Generate a "description" summarizing the dish.
                    - Ensure "tags" is a JSON array of exactly 8 strings, inferring from context if needed (e.g., ["Chinese", "Pork", ...]).
                    - Ensure the JSON is complete with all closing braces.

                    Schema: {schema}

                    Recipe Text: {text}
                """
            },
        ],
        format=Response.model_json_schema(),  # Pass the schema
    )
    data = response.message.content
    print(data)
    return data
    
if __name__ == "__main__":
    urls = [
        # "https://www.justonecookbook.com/bamboo-rice-takenoko-gohan/",
        "https://redhousespice.com/red-cooked-pork-belly/",
        # "https://www.thefrenchcookingacademy.com/recipes/sauce-entrecote"
    ]
    for url in urls:
            logger.info(f"trying url at {url}")
            recipe = scrape_recipe(url)
            #recipe_text = json.dumps(recipe, indent=2)
            # print(recipe)
            ollama_parse(recipe, url)