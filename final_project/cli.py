class Cli:
	def _format_agent_msg(self, content: str) -> None:
		return f'\033[38;2;152;251;152m{content}\033[0m'

	def print_msg(self, msg: dict[str, str]) -> None:
		if msg['role'] == 'assistant':
			print(self._format_agent_msg(msg['content']))

	def flush(self):
		print("\033[H\033[J", end="")
