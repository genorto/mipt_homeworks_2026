from agent.agent import Agent
from agent.config import Config
from cli import Cli
from utils.constants import (
    QUIT,
    RESET,
    FILE_CHUNK,
    ASK_PROMPT,
    ENTER_FILE_PATH,
    TYPE_USER_PROMPT,
    ENTER_TO_CONTINUE,
    FILE_PROCESSED,
)
from utils.message import SYSTEM, create_msg
from utils.files import FileException, read_file, insert_files
from utils.chunks import (
    FORCE,
    FileChunkParams,
    ParamsException,
    format_file_chunk_params,
    divide_by_chunks,
)


class App:
    agent: Agent
    cli: Cli

    def __init__(self) -> None:
        config = Config()
        self.agent = Agent(config)
        self.cli = Cli()

    def _reset(self) -> None:
        self.agent.reset()
        self.cli.flush()

    def _process_chunks(self, user_prompt: str, raw_chunks: str, params: FileChunkParams) -> None:
        chunks = divide_by_chunks(raw_chunks, params)
        for chunk in chunks:
            response = self.agent.process_chunk(user_prompt, chunk)
            if response:
                self.cli.print_msg(response)
            if params[FORCE]:
                continue
            self.cli.print_msg(create_msg(SYSTEM, ENTER_TO_CONTINUE))
            input()

    def _file_chunk(self, raw_params: str) -> None:
        try:
            params = format_file_chunk_params(raw_params)
            self.cli.print_msg(create_msg(SYSTEM, ENTER_FILE_PATH))
            content = read_file(input())
            self.cli.print_msg(create_msg(SYSTEM, TYPE_USER_PROMPT))
            self._process_chunks(input(), content, params)
            self.cli.print_msg(create_msg(SYSTEM, FILE_PROCESSED))
        except (ParamsException, FileException) as e:
            self.cli.print_msg(create_msg(SYSTEM, str(e)))

    def run(self) -> None:
        self.cli.flush()
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
                self._file_chunk(args)
                continue
            try:
                content = insert_files(query)
            except FileException as e:
                self.cli.print_msg(create_msg(SYSTEM, str(e)))
                continue
            response = self.agent.request(content)
            if response:
                self.cli.print_msg(response)
            else:
                print()
