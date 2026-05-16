from dataclasses import dataclass
import os
import yaml

@dataclass
class Config:
    api_host: str
    api_key: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str
    model: str

    def __init__(self):
        with open("config.yaml") as file:
            yaml_config = yaml.safe_load(file)
        self.api_host = (
            os.environ.get("API_HOST")
            or yaml_config.get("api_host")
        )
        self.api_key = (
            os.environ.get("API_KEY")
            or yaml_config.get("api_key")
        )
        _limit_message = (
            os.environ.get("LIMIT_MESSAGE")
            or yaml_config.get("limit_message")
        )
        self.limit_message = int(_limit_message) if _limit_message else None
        _limit_chars = (
            os.environ.get("LIMIT_CHARS")
            or yaml_config.get("limit_chars")
        )
        self.limit_chars = int(_limit_chars) if _limit_chars else None
        self.temperature = float(
            os.environ.get("TEMPERATURE")
            or yaml_config.get("temperature")
        )
        self.system_prompt = (
            os.environ.get("SYSTEM_PROMPT")
            or yaml_config.get("system_prompt")
        )
        self.model = (
            os.environ.get("MODEL")
            or yaml_config.get("model")
        )
