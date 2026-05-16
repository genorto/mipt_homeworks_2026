from agent.agent import Agent
from cli import Cli
from agent.config import Config

class App:
	agent: Agent
	cli: Cli

	def __init__(self):
		config = Config()
		self.agent = Agent(config)
		self.cli = Cli()

	def run(self):
		self.cli.flush()
		query = input()
		while query != '\q':
			match query:
				case '/reset':
					self.agent.reset()
					self.cli.flush()
				case _:
					response = self.agent.request(query)
					self.cli.print_msg(response)
			query = input()
