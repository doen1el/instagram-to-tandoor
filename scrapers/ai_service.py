
import os
from logs import setup_logging
from ai_modules.ai_module_interface import AIModuleInterface
from ai_modules.duck_ai import DuckAIModule
# Hier können weitere AI-Module importiert werden (z.B. ChatGPT)

logger = setup_logging("ai_service")

def get_ai_module():
    module_name = os.getenv("AI_MODULE", "duck_ai")
    if module_name == "duck_ai":
        # DuckAI benötigt einen Browser, z.B. Selenium WebDriver
        # Der Browser muss extern übergeben werden!
        from selenium import webdriver
        browser = webdriver.Chrome() # oder andere Instanz, ggf. anpassen
        return DuckAIModule(browser)
    # elif module_name == "chatgpt":
    #     from ai_modules.chatgpt import ChatGPTModule
    #     return ChatGPTModule(...)
    else:
        raise ValueError(f"Unknown AI module: {module_name}")

ai_module = None

def initialize_ai_module():
    global ai_module
    if ai_module is None:
        ai_module = get_ai_module()

def initialize_chat(caption):
    initialize_ai_module()
    return ai_module.initialize_chat(caption)

def send_raw_prompt(prompt):
    initialize_ai_module()
    return ai_module.send_raw_prompt(prompt)

def send_json_prompt(prompt):
    initialize_ai_module()
    return ai_module.send_json_prompt(prompt)

def get_number_of_steps(caption=None):
    initialize_ai_module()
    return ai_module.get_number_of_steps(caption)

def process_recipe_part(part, mode="", step_number=None):
    initialize_ai_module()
    return ai_module.process_recipe_part(part, mode, step_number)