from utils.message import AGENT, ROLE, CONTENT, Message


# light green
def _format_agent_msg(content: str) -> str:
    return f'\033[38;2;152;251;152m{content}\033[0m'


# dark blue
def _format_system_msg(content: str) -> str:
    return f'\033[94m{content}\033[0m'


class Cli:
    def print_msg(self, msg: Message) -> None:
        if msg[ROLE] == AGENT:
            print(_format_agent_msg(msg[CONTENT]))
            return
        print(_format_system_msg(msg[CONTENT]))

    def flush(self) -> None:
        print('\033[H\033[J', end='')
