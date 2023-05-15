import openai
from src.config import Config
from src.loggable import Loggable


cfg = Config()

class Prompt(Loggable):
    def __init__(self):
        super().__init__()

    def send(self, max_tokens=None, stop=None):
        response = openai.ChatCompletion.create(
            model=cfg.model,
            messages=self.log_data,
            max_tokens=max_tokens,
            stop=stop
        )

        return response