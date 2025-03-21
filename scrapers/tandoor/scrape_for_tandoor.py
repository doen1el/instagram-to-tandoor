import json
from scrapers.social_scraper import get_caption_from_post
from scrapers.tandoor.duckai_tandoor import prompt_chatgpt, get_number_of_steps
from scrapers.tandoor.tandoor_api import send_to_tandoor


def scrape_recipe_for_tandoor(url, platform):
    """
    Function to process an Instagram post URL and extract recipe information.
    Args:
        url (str): The URL of the Instagram post containing the recipe.
    The function performs the following steps:
    1. Extracts the caption from the Instagram post.
    2. Determines the number of steps in the recipe from the caption.
    3. Initializes a JSON structure to store the recipe information.
    4. Uses a duck ai to extract and populate various parts of the recipe:
        - Recipe name and description
        - Instructions and ingredients for each step
        - Servings information
        - Nutrition and other metadata
    5. Updates the JSON structure with the extracted information.
    6. Sends the JSON structure to the Tandoor API.
    Returns:
        None
    """
    
    caption, thumbnail_filename = get_caption_from_post(url, platform)
    if caption:
        number_of_steps = get_number_of_steps(caption)
        print(f"Number of steps in the recipe: {number_of_steps}")
        if number_of_steps:
            json_parts = [
                {
                    "name": "string",
                    "description": "string",
                    "keywords": [
                        {
                        "name": "string",
                        "description": "string"
                        }
                    ],
                },
                {
                "name": "string",
                "instruction": "string",
                "ingredients": [
                    {
                    "food": {
                        "name": "string",
                        "plural_name": "string"
                    },
                    "unit": {
                        "name": "string",
                        "plural_name": "string",
                        "description": "string",
                        "base_unit": "string",
                        "open_data_slug": "string"
                    },
                    "amount": "string",
                    "note": "string",
                    "order": 0,
                    "is_header": True,
                    "no_amount": True
                    }
                ],
                "time": 0,
                "order": 0,
                "show_as_header": True,
                "show_ingredients_table": True
                },
                {
                    "servings": 0,
                    "servings_text": "string"
                },
                {
                    "working_time": 0,
                    "waiting_time": 0,
                    "source_url": "string",
                    "internal": True,
                    "show_ingredient_overview":  True,
                } 
            ]
        
            full_json = {}
            
            name_res = prompt_chatgpt(caption, json_parts[0])
            if name_res:
                full_json.update(name_res)
                    
            print(json.dumps(full_json, indent=2))
                    
            steps = {"steps": []}
            for i in range(1, number_of_steps + 1):
                instruction_res = prompt_chatgpt(caption, json_parts[1], True, i)
                if instruction_res:
                    steps["steps"].append(instruction_res)
                print(json.dumps(steps, indent=2))
            
            full_json.update(steps)
            print(json.dumps(full_json, indent=2))
            
            servings_res = prompt_chatgpt(caption, json_parts[2])
            if servings_res:
                full_json.update(servings_res)
                
            print(json.dumps(full_json, indent=2))
                
            nutrition_res = prompt_chatgpt(caption, json_parts[3])
            if nutrition_res:
                full_json.update(nutrition_res)
                
            full_json["source_url"] = url
            
            for step in full_json.get("steps", []):
                for ingredient in step.get("ingredients", []):
                    ingredient["is_header"] = False
                            
            print(json.dumps(full_json, indent=2))
            with open('./scrapers/tandoor/final_json.json', 'w') as outfile:
                json.dump(full_json, outfile, indent=2)
                
            send_to_tandoor(full_json, thumbnail_filename)