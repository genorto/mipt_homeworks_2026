from agent.gateway import Gateway
from agent.config import Config

class Agent:
	limit_message: int | None
	limit_chars: int | None
	system_prompt: dict[str, str]
	gateway: Gateway
	history: list[dict[str, str]]
	count_char: int

	def _create_msg(self, role: str, content: str) -> dict[str, str]:
		return {
			'role': role,
			'content': content,
		}

	def __init__(self, config: Config):
		self.limit_message = config.limit_message
		self.limit_chars = config.limit_chars
		self.system_prompt = self._create_msg('system', config.system_prompt)
		self.gateway = Gateway(config)
		self.history = []
		self.count_char = 0

	def _pop_first(self) -> None:
		self.count_char -= len(self.history[0])
		self.history = self.history[1:]

	def _cut_first(self, count: int) -> None:
		self.count_char -= count
		self.history[0]['content'] = self.history[0]['content'][count:]

	def _add_message_to_history(self, msg: dict[str, str]) -> None:
		self.count_char += len(msg['content'])
		self.history.append(msg)
		if self.limit_message and (len(self.history) > self.limit_message):
			self._pop_first()
		if self.limit_chars is None:
			return
		while (self.count_char > self.limit_chars) and self.history:
			diff = self.count_char - self.limit_chars
			if len(self.history[0]['content']) < diff:
				self._pop_first()
			else:
				self._cut_first(diff)

	def _get_response(self) -> str:
		request_content = [self.system_prompt] + self.history
		return self.gateway.request(request_content)

	def request(self, content: str) -> dict[str, str]:
		user_msg = self._create_msg('user', content)
		self._add_message_to_history(user_msg)
		response = self._get_response()
		response_msg = self._create_msg('assistant', response)
		self._add_message_to_history(response_msg)
		return response_msg

	def reset(self):
		self.history = []
		self.count_char = 0
