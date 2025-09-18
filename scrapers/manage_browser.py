import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from logs import setup_logging
import requests

logger = setup_logging("manage_browser")

def open_browser(url=None, platform=None):
    """
    Opens a browser window and navigates to the specified URL.
    If no URL is provided, navigates to Duck AI website.
    
    Args:
        url (str, optional): URL to navigate to. Defaults to Duck.ai.
        platform (str, optional): Platform type ("instagram", "tiktok") for specific handling.
    
    Returns:
        WebDriver: The browser window object.
    """
    
    logger.info(f"Opening browser{'for '+platform if platform else ''}")

    match os.getenv("BROWSER"):
        case "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options) 
            logger.info("Using Firefox browser")
        case "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            browser = webdriver.Chrome(options=options)
            logger.info("Using Chrome browser")
        case "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless")
            browser = webdriver.Edge(options=options)
            logger.info("Using Edge browser")
        case "safari":
            options = webdriver.SafariOptions()
            options.add_argument("--headless")
            browser = webdriver.Safari(options=options)
            logger.info("Using Safari browser")
        case "docker":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            service = webdriver.firefox.service.Service(executable_path="/usr/local/bin/geckodriver")
            browser = webdriver.Firefox(options=options, service=service)
            logger.info("Using Firefox browser in Docker environment")
        case _:
            options = webdriver.FirefoxOptions()
            browser = webdriver.Firefox(options=options)
            logger.info("Using default Firefox browser")

    # Navigate to specified URL or Duck.ai
    target_url = url if url else "https://duck.ai/"
    logger.info(f"Navigating to {target_url}")
    browser.get(target_url)
    
    # Handle platform-specific setup
    if platform == "instagram" or platform == "i":
        try:
            logger.info("Waiting for Instagram overlay element to appear")
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "xzkaem6"))
            )
            div = browser.find_element(By.CLASS_NAME, "xzkaem6")
            browser.execute_script("arguments[0].style.visibility='hidden'", div)
            logger.info("Successfully hidden Instagram overlay")
        except Exception as e:
            logger.info(f"Failed to hide Instagram overlay: {e}")
    
    # If Duck.ai, handle welcome screens
    elif not url or "duck.ai" in target_url:
        try:
            logger.info("Navigating through Duck.ai welcome screens")
            start_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div[2]/div/button"))
            )
            start_button.click()
            
            continue_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div[3]/div/button"))
            )
            continue_button.click()
        except Exception as e:
            logger.error(f"Failed to navigate Duck.ai welcome screens: {e}", exc_info=True)
            browser.quit()
            return None
    
    # General wait for content to load
    time.sleep(0.5)
    
    logger.info("Browser initialized successfully")
    return browser
        
def close_browser(browser):
    """
    Closes the browser window.
    Args:
        browser (WebDriver): The browser window object to close.
    """
    
    if browser:
        logger.info("Closing browser...")
        try:
            browser.quit()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

def capture_thumbnail(browser, recipe_name=None):
    """
    Attempts to capture a video thumbnail from the current page.
    
    Args:
        browser (WebDriver): The browser window object.
        recipe_name (str, optional): Name of the recipe for image search.
    
    Returns:
        str or None: Path to the thumbnail file if successful, otherwise None.
    """
    if os.getenv("BROWSER") != "docker":
        try:
            logger.info("Attempting to capture video thumbnail")
            # Create thumbnails directory if it doesn't exist
            os.makedirs('thumbnails', exist_ok=True)
            
            # Generate a unique filename
            thumbnail_filename = f"thumbnails/thumbnail_{int(time.time())}.png"
            
            # Wait for video element to be present
            logger.info("Waiting for video element")
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Find the video element
            video = browser.find_element(By.TAG_NAME, "video")
            
            # Take screenshot of the video element
            video.screenshot(thumbnail_filename)
            logger.info(f"Thumbnail saved to {thumbnail_filename}")
            return thumbnail_filename
        except Exception as e:
            logger.info(f"Failed to capture thumbnail: {e}")
            return None
    else:
        # Docker-Umgebung: Fallback-Bild von loremflickr oder Unsplash
        os.makedirs('thumbnails', exist_ok=True)
        thumbnail_filename = f"thumbnails/thumbnail_{int(time.time())}.jpg"
        search_term = recipe_name if recipe_name else "food"
        try:
            logger.info(f"[DOCKER] Attempting to fetch image from loremflickr for: {search_term}")
            url = f"https://loremflickr.com/640/480/{search_term.replace(' ', '%20')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(thumbnail_filename, 'wb') as f:
                    f.write(response.content)
                logger.info(f"[DOCKER] Thumbnail saved to {thumbnail_filename} from loremflickr")
                return thumbnail_filename
            else:
                logger.info(f"[DOCKER] Failed to fetch image from loremflickr, status: {response.status_code}")
        except Exception as e:
            logger.info(f"[DOCKER] Error fetching image from loremflickr: {e}")
        # Fallback: Unsplash (ohne API-Key nur ein generisches Bild)
        try:
            logger.info(f"[DOCKER] Attempting to fetch fallback image from Unsplash")
            unsplash_url = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=640&q=80"
            response = requests.get(unsplash_url, timeout=10)
            if response.status_code == 200:
                with open(thumbnail_filename, 'wb') as f:
                    f.write(response.content)
                logger.info(f"[DOCKER] Thumbnail saved to {thumbnail_filename} from Unsplash fallback")
                return thumbnail_filename
            else:
                logger.info(f"[DOCKER] Failed to fetch fallback image from Unsplash, status: {response.status_code}")
        except Exception as e:
            logger.info(f"[DOCKER] Error fetching fallback image from Unsplash: {e}")
        logger.info(f"[DOCKER] No thumbnail could be generated.")
        return None