from abc import ABC, abstractmethod

class AIModuleInterface(ABC):
	@abstractmethod
	def initialize_chat(self, context):
		pass

	@abstractmethod
	def send_raw_prompt(self, prompt):
		pass

	@abstractmethod
	def send_json_prompt(self, prompt):
		pass

	@abstractmethod
	def get_number_of_steps(self, caption=None):
		pass

	@abstractmethod
	def process_recipe_part(self, part, mode="", step_number=None, context=None):
		pass
