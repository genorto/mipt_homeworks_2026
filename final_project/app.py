from agent.agent import Agent
from agent.config import Config
from cli import Cli
from utils import (
    QUIT,
    RESET,
    FILE_CHUNK,
    SYSTEM,
    ASK_PROMPT,
    ENTER_FILE_PATH,
    TYPE_USER_PROMPT,
    ENTER_TO_CONTINUE,
    FILE_PROCESSED,
    FILE_PATH_PREFIX,
    FILE_PATH_POSTFIX,
    create_msg,
)


def _insert_file(text: str) -> str:
    begin = text.find(FILE_PATH_PREFIX) + 3
    end = text.find(FILE_PATH_POSTFIX, begin + 2)
    file_path = text[begin:end]
    with open(file_path) as file:
        content = file.read()
    target = FILE_PATH_PREFIX + file_path + FILE_PATH_POSTFIX
    return text.replace(target, content)


def _format_query(query: str) -> str:
    while FILE_PATH_PREFIX in query:
        query = _insert_file(query)
    return query


class App:
    agent: Agent
    cli: Cli
    system_prompt: str

    def __init__(self):
        config = Config()
        self.agent = Agent(config)
        self.cli = Cli()
        self.system_prompt = f'System prompt: {config.system_prompt}'

    def _reset(self):
        self.agent.reset()
        self.cli.flush()

    def _process_chunks(self, user_prompt: str, chunks: list[str]) -> None:
        for chunk in chunks:
            response = self.agent.process_chunk(user_prompt, chunk)
            if response:
                self.cli.print_msg(response)
            self.cli.print_msg(create_msg(SYSTEM, ENTER_TO_CONTINUE))
            input()

    def _file_chunk(self) -> None:
        try:
            self.cli.print_msg(create_msg(SYSTEM, ENTER_FILE_PATH))
            with open(input()) as file:
                content = file.read()
            self.cli.print_msg(create_msg(SYSTEM, TYPE_USER_PROMPT))
            self._process_chunks(input(), content.split('\n'))
            self.cli.print_msg(create_msg(SYSTEM, FILE_PROCESSED))
        except KeyboardInterrupt:
            print()

    def run(self):
        self.cli.flush()
        self.cli.print_msg(create_msg(SYSTEM, self.system_prompt))
        while True:
            self.cli.print_msg(create_msg(SYSTEM, ASK_PROMPT))
            query = input()
            if query == QUIT:
                break
            if query == RESET:
                self._reset()
                continue
            name, _, args = query.partition(' ')
            if name == FILE_CHUNK:
                self._file_chunk()
                continue
            content = _format_query(query)
            response = self.agent.request(content)
            if response:
                self.cli.print_msg(response)
            else:
                print()
