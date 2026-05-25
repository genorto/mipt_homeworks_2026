from enum import StrEnum
from typing import Literal, TypedDict

ROLE: Literal['role'] = 'role'
CONTENT: Literal['content'] = 'content'


class Roles(StrEnum):
    SYSTEM = 'system'
    USER = 'user'
    AGENT = 'assistant'


class Message(TypedDict):
    role: str
    content: str


def create_msg(role: str, content: str) -> Message:
    return {
        ROLE: role,
        CONTENT: content,
    }
