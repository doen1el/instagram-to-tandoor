def validate_tandoor_payload(payload, source_url=None):
    """
    Validiert und ergänzt alle Pflichtfelder für Tandoor-API.
    Args:
        payload (dict): Das zu prüfende Rezept-JSON
        source_url (str, optional): Die Quell-URL des Rezepts
    Returns:
        dict: Validiertes und ergänztes Rezept-JSON
    """
    tandoor_required = {
        "name": "Unbenanntes Rezept",
        "description": "",
        "steps": [],
        "keywords": [],
        "image": None,
        "internal": True,
        "show_ingredient_overview": False,
        "servings": 1,
        "servings_text": "",
        "working_time": 0,
        "waiting_time": 0,
        "source_url": source_url or payload.get("source_url", ""),
        "private": False,
        "shared": []
    }
    for key, value in tandoor_required.items():
        if key not in payload or payload[key] is None:
            payload[key] = value
    if not isinstance(payload["steps"], list):
        payload["steps"] = []
    if not isinstance(payload["keywords"], list):
        payload["keywords"] = []
    if not payload["name"]:
        payload["name"] = "Unbenanntes Rezept"
    return payload
import json
import os
from io import BytesIO

import requests as request
from PIL import Image

from logs import setup_logging

logger = setup_logging("recipe_api")

def send_recipe(api_type, json_data, thumbnail_filename):
    """
    Unified function to send a recipe to either Tandoor or Mealie API
    
    Args:
        api_type (str): Type of API to use ("tandoor" or "mealie")
        json_data (dict): Recipe data in JSON format
        thumbnail_filename (str): Path to thumbnail image file
        
    Returns:
        dict: Response information with status and recipe ID
    """
    api_type = api_type.upper()
    
    # Set up API-specific parameters
    base_url = os.getenv(f"BASE_URL_{api_type}")
    token = os.getenv(f"TOKEN_{api_type}")
    api_logger = setup_logging(f"{api_type.lower()}_api")
    
    # Set up API-specific endpoints and behavior
    if api_type == "TANDOOR":
        create_endpoint = "/api/recipe/"
        extract_id = lambda response: response.json().get('id')
        # --- Tandoor: Payload anpassen ---
        # Pflichtfelder laut OpenAPI Spec
        tandoor_defaults = {
            "name": "Unbenanntes Rezept",
            "description": "",
            "steps": [],
            "keywords": [],
            "image": None,
            "internal": True,
            "show_ingredient_overview": False,
            "servings": 1,
            "servings_text": "",
            "working_time": 0,
            "waiting_time": 0,
            "source_url": "",
            "private": False,
            "shared": []
        }
        # Füge fehlende Felder hinzu
        for key, value in tandoor_defaults.items():
            if key not in json_data:
                json_data[key] = value
        # steps muss ein Array von Objekten sein
        if not isinstance(json_data["steps"], list):
            json_data["steps"] = []
        # keywords muss ein Array sein
        if not isinstance(json_data["keywords"], list):
            json_data["keywords"] = []
        # name darf nicht leer sein
        if not json_data["name"]:
            json_data["name"] = "Unbenanntes Rezept"
    elif api_type == "MEALIE":
        create_endpoint = "/api/recipes/create/html-or-json"
        extract_id = lambda response: response.content.decode('utf-8').strip('"')
    else:
        api_logger.error(f"Unknown API type: {api_type}")
        return {"status": "error", "error": f"Unknown API type: {api_type}"}

    # Common headers for both APIs
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    try:
        response = request.post(f'{base_url}{create_endpoint}', 
                              json=json_data, 
                              headers=headers)
        api_logger.info(f"[DEBUG] Response status code: {response.status_code}")
        # Extract recipe ID
        recipe_id = extract_id(response)
        api_logger.info(f"{api_type} Recipe ID: {recipe_id}")
        # Upload thumbnail if available
        api_logger.info(f"Thumbnail File: {thumbnail_filename}")
        api_logger.info(f"Path exists: {os.path.exists(thumbnail_filename)}")
        
        if thumbnail_filename and recipe_id and os.path.exists(thumbnail_filename):
            if api_type == "TANDOOR":
                upload_tandoor_thumbnail(base_url, token, recipe_id, thumbnail_filename, api_logger)
            else:
                upload_mealie_thumbnail(base_url, token, recipe_id, thumbnail_filename, api_logger)
        response.raise_for_status()
        return {
            "status": "success",
            "recipe_id": recipe_id,
            "api_type": api_type
        }

    except request.exceptions.HTTPError as http_err:
        api_logger.error(f"HTTP error occurred: {http_err}")
        api_logger.error(f"Response content: {response.content}")
        return {"status": "error", "error": str(http_err)}
    except request.exceptions.ConnectionError as conn_err:
        api_logger.error(f"Connection error occurred: {conn_err}")
        return {"status": "error", "error": str(conn_err)}
    except request.exceptions.Timeout as timeout_err:
        api_logger.error(f"Timeout error occurred: {timeout_err}")
        return {"status": "error", "error": str(timeout_err)}
    except request.exceptions.RequestException as req_err:
        api_logger.error(f"An error occurred: {req_err}")
        return {"status": "error", "error": str(req_err)}
    except Exception as e:
        api_logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        api_logger.info('Done.')


def upload_tandoor_thumbnail(base_url, token, recipe_id, thumbnail_filename, logger):
    """
    Upload a thumbnail image to an existing Tandoor recipe
    """
    logger.info(f"[DEBUG] upload_tandoor_thumbnail called with base_url={base_url}, token={token}, recipe_id={recipe_id}, thumbnail_filename={thumbnail_filename}")
    headers = {'Authorization': f'Bearer {token}'}
    try:
        logger.info(f"[DEBUG] Opening image file: {thumbnail_filename}")
        # Open and optimize the image
        with Image.open(thumbnail_filename) as img:
            logger.info(f"[DEBUG] Image opened. Mode: {img.mode}, Size: {img.size}")
            # Convert to RGB if needed (in case of PNG with alpha channel)
            if img.mode in ('RGBA', 'LA'):
                logger.info("[DEBUG] Converting image to RGB due to alpha channel.")
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            # Save to a BytesIO object
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            logger.info(f"[DEBUG] Image converted and saved to BytesIO.")
            # Create the multipart form data
            files = {
                'image': (os.path.basename(thumbnail_filename), img_byte_arr, 'image/jpeg')
            }
            logger.info(f"[DEBUG] Sending PUT request to {base_url}/api/recipe/{recipe_id}/image/")
            # Send the request to the specific image endpoint
            response = request.put(
                f'{base_url}/api/recipe/{recipe_id}/image/',
                files=files,
                headers=headers
            )
            logger.info(f"[DEBUG] PUT response status: {response.status_code}")
            logger.info(f"[DEBUG] PUT response text: {response.text}")
            response.raise_for_status()
            logger.info(f"Successfully uploaded thumbnail for Tandoor recipe {recipe_id}")
    except Exception as e:
        logger.error(f"[DEBUG] Failed to upload thumbnail: {e}")
        logger.error(f"Thumbnail path: {thumbnail_filename}")
        logger.error(f"Recipe ID: {recipe_id}")


def upload_mealie_thumbnail(base_url, token, recipe_slug, thumbnail_filename, logger):
    """
    Upload a thumbnail image to an existing Mealie recipe
    """
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Get file extension
        _, extension = os.path.splitext(thumbnail_filename)
        extension = extension.lstrip('.').lower()
        
        # Clean up the recipe slug - remove quotes if present
        recipe_slug = recipe_slug.strip('"\'')
        
        # Prepare the files for upload
        with open(thumbnail_filename, 'rb') as img_file:
            files = {
                'image': (f'image.{extension}', img_file, f'image/{extension}'),
                'extension': (None, extension)
            }
            
            # Send the request
            response = request.put(
                f'{base_url}/api/recipes/{recipe_slug}/image',
                files=files,
                headers=headers
            )
            
            logger.info(f"Image upload response status: {response.status_code}")
            if response.text:
                logger.info(f"Image upload response: {response.text}")
            response.raise_for_status()
            logger.info(f"Successfully uploaded thumbnail for Mealie recipe {recipe_slug}")
            
    except Exception as e:
        logger.error(f"Failed to upload thumbnail: {e}")
        logger.error(f"Thumbnail path: {thumbnail_filename}")
        logger.error(f"Recipe slug: {recipe_slug}")