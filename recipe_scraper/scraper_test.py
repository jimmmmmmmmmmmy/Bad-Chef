from recipe_scraper import scrape_recipe, ollama_parse
import json

urls = [
    "https://www.thefrenchcookingacademy.com/recipes/sauce-entrecote"
]
for url in urls:
        recipe = scrape_recipe(url)
        result = ollama_parse(recipe, url)

        data = json.loads(result)
        with open("test.json", "w") as json_file:
            json.dump(data["recipe"], json_file, indent=4, ensure_ascii=False)