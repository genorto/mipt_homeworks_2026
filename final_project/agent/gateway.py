from agent.config import Config
from openai import OpenAI
from utils.message import Message


class AgentException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class Gateway:
    client: OpenAI
    temperature: float
    model: str

    def __init__(self, config: Config) -> None:
        self.client = OpenAI(
            base_url=config.api_host,
            api_key=config.api_key,
        )
        self.temperature = config.temperature
        self.model = config.model

    def request(self, messages: list[Message]) -> str | None:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except KeyboardInterrupt:
            return None
        except Exception as e:
            raise AgentException(e) from e
