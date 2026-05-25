from agent.gateway import Gateway
from agent.config import Config
from utils.message import Roles, CONTENT, Message, create_msg


class Agent:
    limit_message: int | None
    limit_chars: int | None
    system_prompt: Message | None
    gateway: Gateway
    context: list[Message]
    count_char: int

    def __init__(self, config: Config):
        self.limit_message = config.limit_message
        self.limit_chars = config.limit_chars
        self.system_prompt = (
            create_msg(Roles.SYSTEM, config.system_prompt) if config.system_prompt else None
        )
        self.gateway = Gateway(config)
        self.context = []
        self.count_char = 0

    def _pop_first(self) -> None:
        self.count_char -= len(self.context[0][CONTENT])
        self.context = self.context[1:]

    def _cut_first(self, count: int) -> None:
        self.count_char -= count
        self.context[0][CONTENT] = self.context[0][CONTENT][count:]

    def _add_msg_to_context(self, msg: Message) -> None:
        self.count_char += len(msg[CONTENT])
        self.context.append(msg)

        if self.limit_message and len(self.context) > self.limit_message:
            self._pop_first()

        if self.limit_chars is None:
            return

        while self.count_char > self.limit_chars and self.context:
            diff = self.count_char - self.limit_chars
            if len(self.context[0][CONTENT]) < diff:
                self._pop_first()
            else:
                self._cut_first(diff)

    def _post_context(self) -> str | None:
        if self.system_prompt is None:
            return self.gateway.request(self.context)
        content = [self.system_prompt] + self.context
        return self.gateway.request(content)

    def request(self, content: str) -> Message | None:
        user_msg = create_msg(Roles.USER, content)
        self._add_msg_to_context(user_msg)

        response = self._post_context()
        if response is None:
            return None

        response_msg = create_msg(Roles.AGENT, response)
        self._add_msg_to_context(response_msg)
        return response_msg

    def process_chunk(self, user_prompt: str, chunk: str) -> Message | None:
        user_msg = create_msg(Roles.USER, user_prompt)
        self._add_msg_to_context(user_msg)

        chunk_msg = create_msg(Roles.USER, chunk)
        self._add_msg_to_context(chunk_msg)

        response = self._post_context()
        if response is None:
            return None
        return create_msg(Roles.AGENT, response)

    def reset(self) -> None:
        self.context = []
        self.count_char = 0
