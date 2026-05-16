from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str


class ConfigException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


# commands
QUIT = '\q'
RESET = '/reset'
FILE_CHUNK = '/file_chunk'

# roles
SYSTEM = 'system'
USER = 'user'
AGENT = 'assistant'

# system messages
ASK_PROMPT = 'Please, enter your prompt:'
ENTER_FILE_PATH = 'Enter file path...'
TYPE_USER_PROMPT = 'Type user prompt...'
ENTER_TO_CONTINUE = '< Enter to continue >'
FILE_PROCESSED = 'File processed successfully.'

# message params
ROLE = 'role'
CONTENT = 'content'


# file path
FILE_PATH_PREFIX = '@::'
FILE_PATH_POSTFIX = '::'


def create_msg(role: str, content: str) -> Message:
    return {
        ROLE: role,
        CONTENT: content,
    }
