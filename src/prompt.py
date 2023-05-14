import openai
from src.config import Config
from src.loggable import Loggable


cfg = Config()

class Prompt(Loggable):
    def __init__(self):
        super().__init__()

    def send(self, stop=None):
        response = openai.ChatCompletion.create(
            model=cfg.model,
            messages=self.log_data,
            stop=stop
        )

        return response