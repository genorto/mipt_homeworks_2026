from agent.config import Config
from openai import OpenAI

class Gateway:
	client: OpenAI
	temperature: float
	model: str

	def __init__(self, config: Config):
		self.client = OpenAI(
			base_url=config.api_host,
		  api_key=config.api_key,
		)
		self.temperature = config.temperature
		self.model = config.model

	def request(self, messages: list[dict[str, str]]) -> str:
		response = self.client.chat.completions.create(
    	model=self.model,
    	messages=messages,
			temperature=self.temperature
		)
		return response.choices[0].message.content
