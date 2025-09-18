
import os
from logs import setup_logging
from scrapers.ai_modules.duck_ai import DuckAIModule
from scrapers.ai_modules.chat_gpt import ChatGPTModule

logger = setup_logging("ai_service")

def get_ai_module():
    module_name = os.getenv("AI_MODULE", "duck_ai")
    if module_name == "duck_ai":
        from selenium import webdriver
        browser = webdriver.Chrome()
        return DuckAIModule(browser)
    elif module_name == "openai":
        return ChatGPTModule()
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

def process_recipe_part(part, mode="", step_number=None, context=None):
    initialize_ai_module()
    return ai_module.process_recipe_part(part, mode, step_number, context)