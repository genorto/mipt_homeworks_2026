import os
import yaml
from dataclasses import dataclass
from utils.constants import DEFAULT_TEMPERATURE


class ConfigException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def _is_positive_integer(raw_limit: str) -> None:
    try:
        limit = int(raw_limit)
        if limit <= 0:
            raise ConfigException('Incorrect limit.')
    except ValueError as e:
        raise ConfigException('Incorrect limit.') from e


def _is_fraction(raw_temperature: str) -> None:
    try:
        temperature = float(raw_temperature)
        if temperature < 0 or temperature > 1:
            raise ConfigException('Incorrect temperature.')
    except ValueError as e:
        raise ConfigException('Incorrect temperature.') from e


def _convert_limit(raw_limit: str | None) -> int | None:
    if raw_limit is None:
        return None
    _is_positive_integer(raw_limit)
    return int(raw_limit)


def _convert_temperature(raw_temperature: str | None) -> float:
    if raw_temperature is None:
        return DEFAULT_TEMPERATURE
    _is_fraction(raw_temperature)
    return float(raw_temperature)


@dataclass
class Config:
    api_host: str
    api_key: str
    limit_message: int | None
    limit_chars: int | None
    model: str
    temperature: float
    system_prompt: str | None

    def __init__(self) -> None:
        try:
            with open('config.yaml') as file:
                yaml_config = yaml.safe_load(file) or {}
        except FileNotFoundError:
            yaml_config = {}
        api_host: str | None = os.environ.get('API_HOST') or yaml_config.get('api_host')
        if api_host is None:
            raise ConfigException('No URL provided.')
        self.api_host = api_host
        api_key: str | None = os.environ.get('API_KEY') or yaml_config.get('api_key')
        if api_key is None:
            raise ConfigException('No API key provided.')
        self.api_key = api_key
        self.limit_message = _convert_limit(
            os.environ.get('LIMIT_MESSAGE') or yaml_config.get('limit_message')
        )
        self.limit_chars = _convert_limit(
            os.environ.get('LIMIT_CHARS') or yaml_config.get('limit_chars')
        )
        model: str | None = os.environ.get('MODEL') or yaml_config.get('model')
        if model is None:
            raise ConfigException('No model provided.')
        self.model = model
        self.temperature = _convert_temperature(
            os.environ.get('TEMPERATURE') or yaml_config.get('temperature')
        )
        self.system_prompt = yaml_config.get('system_prompt')
