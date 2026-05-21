from app import App
from agent.config import ConfigException

if __name__ == '__main__':
    try:
        app = App()
        app.run()
    except ConfigException as e:
        print(e)
