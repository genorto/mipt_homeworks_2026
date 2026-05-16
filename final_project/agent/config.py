from dataclasses import dataclass
import os
import yaml
from utils import ConfigException


def _validate_limit(raw_limit: str) -> None:
    try:
        limit = int(raw_limit)
        if limit <= 0:
            raise ConfigException('Incorrect limit.')
    except TypeError as e:
        raise ConfigException('No limit provided.') from e
    except ValueError as e:
        raise ConfigException('Incorrect limit.') from e


def _validate_temperature(raw_temperature: str) -> None:
    try:
        temperature = float(raw_temperature)
        if temperature < 0 or temperature > 1:
            raise ConfigException('Incorrect temperature.')
    except TypeError as e:
        raise ConfigException('No temperature provided.') from e
    except ValueError as e:
        raise ConfigException('Incorrect temperature.') from e


@dataclass
class Config:
    def __init__(self):
        with open('config.yaml') as file:
            yaml_config = yaml.safe_load(file)
        self.api_host = os.environ.get('API_HOST') or yaml_config.get('api_host')
        if self.api_host is None:
            raise ConfigException('No URL provided.')
        self.api_key = os.environ.get('API_KEY') or yaml_config.get('api_key')
        if self.api_key is None:
            raise ConfigException('No API key provided.')
        limit_message = os.environ.get('LIMIT_MESSAGE') or yaml_config.get('limit_message')
        _validate_limit(limit_message)
        self.limit_message = int(limit_message)
        limit_chars = os.environ.get('LIMIT_CHARS') or yaml_config.get('limit_chars')
        _validate_limit(limit_chars)
        self.limit_chars = int(limit_chars)
        self.model = os.environ.get('MODEL') or yaml_config.get('model')
        if self.model is None:
            raise ConfigException('No model provided.')
        temperature = os.environ.get('TEMPERATURE') or yaml_config.get('temperature')
        _validate_temperature(temperature)
        self.temperature = temperature
        self.system_prompt = os.environ.get('SYSTEM_PROMPT') or yaml_config.get('system_prompt')
        if self.system_prompt is None:
            raise ConfigException('No system prompt provided.')
