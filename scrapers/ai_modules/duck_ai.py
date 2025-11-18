import os
import re
import json
from bs4 import BeautifulSoup
from logs import setup_logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .ai_module_interface import AIModuleInterface

class DuckAIModule(AIModuleInterface):
	def __init__(self, browser):
		self.browser = browser
		self.logger = setup_logging("duck_ai")

	def initialize_chat(self, caption):
		self.logger.info("Initializing chat with recipe context...")
		try:
			textarea = WebDriverWait(self.browser, 10).until(
				EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
			)
			context_prompt = f"I'm going to ask you questions about this recipe. Please use this recipe information as context for all your responses: {caption}"
			textarea.send_keys(context_prompt)
			textarea.send_keys(Keys.RETURN)
			WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @disabled]")))
			WebDriverWait(self.browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button//rect[@width='10' and @height='10']")))
			self.logger.info("Chat initialized successfully with recipe context")
			return True
		except Exception as e:
			self.logger.error(f"Failed to initialize chat: {e}", exc_info=True)
			return False

	def send_raw_prompt(self, prompt):
		self.logger.info(f"Sending raw prompt: {prompt[:50]}...")
		try:
			textarea = WebDriverWait(self.browser, 15).until(
				EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
			)
			WebDriverWait(self.browser, 15).until(
				EC.element_to_be_clickable((By.XPATH, "//textarea[@name='user-prompt']"))
			)
			textarea.clear()
			textarea.send_keys(prompt)
			textarea.send_keys(Keys.RETURN)
			WebDriverWait(self.browser, 60).until(
				EC.element_to_be_clickable((By.XPATH, "//textarea[@name='user-prompt']"))
			)
			self.logger.info("Response generation completed")
			response = self.browser.page_source
			return response
		except Exception as e:
			self.logger.error(f"Failed to send prompt: {e}", exc_info=True)
			return None

	def extract_json_from_response(self, response):
		if not response:
			return None
		try:
			soup = BeautifulSoup(response, 'html.parser')
			code_blocks = soup.find_all('code', {'class': 'language-json'})
			if code_blocks:
				json_response = code_blocks[-1].get_text()
				return json.loads(json_response)
			else:
				self.logger.warning("No JSON code block found in the response")
				return None
		except Exception as e:
			self.logger.error(f"Failed to extract JSON: {e}", exc_info=True)
			return None

	def send_json_prompt(self, prompt):
		response = self.send_raw_prompt(prompt)
		return self.extract_json_from_response(response)

	def get_number_of_steps(self, caption=None):
		self.logger.info("Getting number of recipe steps...")
		try:
			prompt = "How many steps are in this recipe? Please respond with only a number."
			response = self.send_raw_prompt(prompt)
			if response:
				soup = BeautifulSoup(response, 'html.parser')
				response_divs = soup.find_all('div', {'class': 'VrBPSncUavA1d7C9kAc5'})
				if response_divs:
					last_response_div = response_divs[-1]
					paragraph = last_response_div.find('p')
					if paragraph:
						text = paragraph.get_text().strip()
						numbers = re.findall(r'\d+', text)
						if numbers:
							number_of_steps = int(numbers[0])
							self.logger.info(f"Found {number_of_steps} steps in the recipe")
							return number_of_steps
						else:
							self.logger.warning(f"No number found in response: {text}")
					else:
						self.logger.warning("No paragraph found in response")
				else:
					self.logger.warning("No response divs found")
			self.logger.warning("Could not determine number of steps")
			return None
		except Exception as e:
			self.logger.error(f"Error in get_number_of_steps: {e}", exc_info=True)
			return None

	def process_recipe_part(self, part, mode="", step_number=None, context=None):
		try:
			if mode == "step" or step_number is not None:
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part}. Only complete the specified sections. Only complete step {step_number} of the recipe. If the step has more than 3 ingredients, only complete the first 3 and finish the JSON object. The name of the step should be the step number e.g. 'name': '{step_number}.'. Only include the current instruction description in the instruction field. The amount value of the ingredient can only be a whole number or a decimal NOT A FRACTION (convert it to a decimal). If an ingredient has already been mentioned in a previous step, do not include it again as an ingredient in this step. Respond with a JSON code block enclosed in triple backticks (```json)."
			elif mode == "info":
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Only fill out author, description, recipeYield, prepTime and cooktime. The cooktime and pretime should have the format e.g. PT1H for one hour or PT15M for 15 Minutes."
			elif mode == "ingredients":
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Append the ingredients to the 'recipeIngredient' list. One ingredient per line."
			elif mode == "name":
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Keep the name of the recipe short."
			elif mode == "nutrition":
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Only fill out calories and fatContent with a string."
			elif mode == "instructions":
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Write the instruction as one long string. No string separation, just one long text! Don't add ingredients here. JSON FORMAT IN CODE WINDOW!"
			else:
				prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part}. Only complete the specified sections of the document. Ensure the response is formatted as a JSON code block enclosed in triple backticks (```json)."
			result = self.send_json_prompt(prompt)
			if result:
				self.logger.info(f"{mode if mode else 'General'} data processed successfully")
				return result
			else:
				self.logger.warning(f"No valid response for {mode if mode else 'general'} data")
				return None
		except Exception as e:
			self.logger.error(f"Error processing {mode if mode else 'recipe part'}: {e}", exc_info=True)
			return None
