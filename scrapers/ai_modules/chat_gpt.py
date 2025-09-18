import os
import json
import re
import openai
from .ai_module_interface import AIModuleInterface

class ChatGPTModule(AIModuleInterface):
    def __init__(self, api_key=None, model="gpt-5"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        openai.api_key = self.api_key
        self.context = None

    def initialize_chat(self, context):
        self.context = context
        return True

    def send_raw_prompt(self, prompt):
        messages = []
        if self.context:
            messages.append({"role": "system", "content": f"Recipe context: {self.context}"})
        messages.append({"role": "user", "content": prompt})
        response = openai.resources.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message["content"]

    def send_json_prompt(self, prompt):
        raw = self.send_raw_prompt(prompt)
        # Extrahiere JSON aus Antwort (triple backticks oder code block)
        match = re.search(r"```json\\s*(.*?)```", raw, re.DOTALL)
        if not match:
            match = re.search(r"{.*}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                return None
        return None

    def get_number_of_steps(self, caption=None):
        self.initialize_chat(caption)
        prompt = "How many steps are in this recipe? Please respond with only a number."
        raw = self.send_raw_prompt(prompt)
        numbers = re.findall(r"\\d+", raw)
        return int(numbers[0]) if numbers else None

    def process_recipe_part(self, part, mode="", step_number=None):
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
        return self.send_json_prompt(prompt)