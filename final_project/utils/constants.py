from enum import StrEnum


class Commands(StrEnum):
    QUIT = '\q'
    RESET = '/reset'
    FILE_CHUNK = '/filechunk'


class SystemMessages(StrEnum):
    ASK_PROMPT = 'Please, enter your prompt:'
    ENTER_FILE_PATH = 'Enter file path...'
    TYPE_USER_PROMPT = 'Type user prompt...'
    ENTER_TO_CONTINUE = '< Enter to continue >'
    FILE_PROCESSED = 'File processed successfully.'
    UNEXPECTED_ERROR = 'Unexpected error occurred: '


DEFAULT_TEMPERATURE = 0.5
