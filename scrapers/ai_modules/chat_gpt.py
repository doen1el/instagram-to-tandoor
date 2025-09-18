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
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def send_json_prompt(self, prompt):
        raw = self.send_raw_prompt(prompt)
        print(f"[DEBUG] GPT raw response:\n{raw}")
        # Extrahiere JSON aus Antwort (triple backticks oder code block)
        match = re.search(r"```json\s*(.*?)```", raw, re.DOTALL)
        if not match:
            match = re.search(r"({.*})", raw, re.DOTALL)  # mit Gruppe
        match_content = match.group(1) if match and match.lastindex == 1 else None
        print(f"[DEBUG] Regex match: {match_content}")
        if match_content:
            try:
                parsed = json.loads(match_content)
                print(f"[DEBUG] Parsed JSON: {parsed}")
                return parsed
            except Exception as e:
                print(f"[DEBUG] JSON parsing error: {e}")
                return None
        print("[DEBUG] No valid JSON found in response.")
        return None

    def get_number_of_steps(self, caption=None):
        self.initialize_chat(caption)
        prompt = (
            "How many steps are in this recipe? Respond only with a single integer. "
            "Do not include any explanation, text, units, or formatting. Only reply with the number."
        )
        max_attempts = 3
        for attempt in range(max_attempts):
            raw = self.send_raw_prompt(prompt)
            print(f"[DEBUG] get_number_of_steps attempt {attempt+1}: {raw}")
            # Nur eine reine Zahl akzeptieren
            match = re.fullmatch(r"\s*(\d+)\s*", raw)
            if match:
                return int(match.group(1))
            # Fallback: Zahl irgendwo im Text suchen
            numbers = re.findall(r"\d+", raw)
            if numbers:
                return int(numbers[0])
        print("[DEBUG] Failed to extract number of steps after 3 attempts.")
        return None

    def process_recipe_part(self, part, mode="", step_number=None, context=None):
        # Kontext einfügen
        context_str = ""
        if context:
            if isinstance(context, dict):
                context_str = f"Recipe context (JSON): {json.dumps(context, ensure_ascii=False)}\n"
            else:
                context_str = f"Recipe context: {context}\n"
        if mode == "step" or step_number is not None:
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Fill out the following fields for step {step_number} of the recipe: 'name', 'instruction', 'ingredients', 'time', 'order', 'show_as_header', 'show_ingredients_table'.\n"
                f"- 'name' should be the step number, e.g. 'name': '{step_number}.'\n"
                f"- 'instruction' should be a clear, short description of the step.\n"
                f"- 'ingredients' should be a list of ingredient objects (max 3 per step).\n"
                f"- 'amount' must be a whole number or decimal, NOT a fraction.\n"
                f"- Do NOT repeat ingredients from previous steps.\n"
                f"- Example format: ```json {{'name': '1.', 'instruction': 'Chop onions.', 'ingredients': [{{'food': {{'name': 'onion'}}, 'amount': '1', ...}}], 'time': 5, 'order': 1, 'show_as_header': false, 'show_ingredients_table': true}}```\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        elif mode == "info":
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Fill out the fields: 'author', 'description', 'recipeYield', 'prepTime', 'cooktime'.\n"
                f"- 'prepTime' and 'cooktime' format: PT1H for one hour, PT15M for 15 minutes.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        elif mode == "ingredients":
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Append the ingredients to the 'recipeIngredient' list. One ingredient per line.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        elif mode == "name":
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Fill out the field 'name' with a short, clear recipe name.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        elif mode == "nutrition":
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Fill out the fields: 'calories' and 'fatContent' as strings.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        elif mode == "instructions":
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Write the instruction as one long string. No string separation, just one long text! Don't add ingredients here.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        else:
            prompt = (
                f"{context_str}"
                f"Please respond ONLY with a valid JSON code block (```json ... ```).\n"
                f"Fill out the specified sections of the document.\n"
                f"Language: {os.getenv('LANGUAGE_CODE', 'en')}\n"
                f"JSON template: {part}"
            )
        return self.send_json_prompt(prompt)