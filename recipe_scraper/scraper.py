from recipe_scraper import scrape_recipe, ollama_parse
import json

urls = [
    # Website
]
for url in urls:
        recipe = scrape_recipe(url)
        result = ollama_parse(recipe, url)
        data = json.loads(result)

        with open("test.json", "r+") as json_file:

            file_data=json.load(json_file)
            file_data["recipes"].append(data)

        with open("test.json", 'w') as json_file:
            json.dump(file_data, json_file, indent=4, ensure_ascii=False)