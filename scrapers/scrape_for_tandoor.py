import json

from logs import setup_logging
from scrapers.ai_service import get_number_of_steps, initialize_chat, process_recipe_part
from scrapers.api_service import send_recipe
from scrapers.social_scraper import get_caption_from_post

logger = setup_logging("scrape_for_tandoor")

def scrape_recipe_for_tandoor(url, platform):
    """
    Process an Instagram or TikTok post URL and extract recipe information.
    Uses a single browser instance for all Duck.ai interactions.
    
    Args:
        url (str): The URL of the social media post containing the recipe.
        platform (str): The platform ('instagram' or 'tiktok').
    
    Returns:
        dict: Result information including URL and status.
        
    Raises:
        Exception: If processing fails.
    """
    
    result = get_caption_from_post(url, platform)
    
    if result is None:
        logger.error("No caption or image found")
        raise Exception("No caption or image found")
    
    caption, thumbnail_filename = result
    logger.info(f"Caption extracted successfully ({len(caption)} chars)")
    
    try:
        # Initialisiere AI-Kontext
        if not initialize_chat(caption):
            logger.error("Failed to initialize chat with recipe context")
            raise Exception("Failed to initialize chat with recipe context")

        # Get the number of steps in the recipe
        number_of_steps = get_number_of_steps(caption)
        if not number_of_steps:
            logger.error("Failed to determine number of steps in recipe")
            raise Exception("Failed to determine number of steps in recipe")

        logger.info(f"Recipe has {number_of_steps} steps")

        # Define JSON templates for different parts of the recipe
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
            },
            {
                "working_time": 0,
                "waiting_time": 0,
                "source_url": "string",
                "internal": True,
                "show_ingredient_overview": True,
            } 
        ]

        # Build the recipe JSON structure
        full_json = {}

        # Get recipe name and description
        logger.info("Getting recipe name and description")
        name_res = process_recipe_part(json_parts[0])
        if name_res:
            full_json.update(name_res)
            logger.info(f"Recipe name: {name_res.get('name', 'Unknown')}")
        else:
            logger.warning("Failed to get recipe name and description")

        # Get recipe steps and ingredients
        logger.info("Getting recipe steps and ingredients")
        steps = {"steps": []}
        for i in range(1, number_of_steps + 1):
            logger.info(f"Processing step {i}/{number_of_steps}")
            instruction_res = process_recipe_part(json_parts[1], "step", i)
            if instruction_res:
                steps["steps"].append(instruction_res)
                logger.info(f"Step {i} processed successfully")
            else:
                logger.warning(f"Failed to process step {i}")

        full_json.update(steps)

        # Get serving information
        logger.info("Getting serving information")
        servings_res = process_recipe_part(json_parts[2])
        if servings_res:
            full_json.update(servings_res)
            logger.info(f"Servings: {servings_res.get('servings', 'Unknown')}")
        else:
            logger.warning("Failed to get serving information")

        # Get nutrition and timing information
        logger.info("Getting nutrition and timing information")
        nutrition_res = process_recipe_part(json_parts[3])
        if nutrition_res:
            full_json.update(nutrition_res)
            logger.info("Nutrition and timing information processed successfully")
        else:
            logger.warning("Failed to get nutrition and timing information")

        # Add source URL
        full_json["source_url"] = url

        # Fix ingredient header flags
        for step in full_json.get("steps", []):
            for ingredient in step.get("ingredients", []):
                ingredient["is_header"] = False

        # Save the final JSON
        logger.info("Saving final JSON")
        with open('./scrapers/final_json.json', 'w') as outfile:
            json.dump(full_json, outfile, indent=2)

        # Send to Tandoor
        logger.info("Sending to Tandoor API")
        tandoor_result = send_recipe("TANDOOR", full_json, thumbnail_filename)

        return tandoor_result

    except Exception as e:
        logger.error(f"Error processing recipe: {e}", exc_info=True)
        raise