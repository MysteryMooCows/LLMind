import openai
from src.config import Config

cfg = Config()


# This is a magic function that can do anything with no-code. See
# https://github.com/Torantulino/AI-Functions for more info.
def call_ai_function(function, args, description, model=None) -> str:
    """Call an AI function"""
    if model is None:
        model = cfg.smart_llm_model

    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]

    # parse args to comma separated string
    args = ", ".join(args)
    messages = [
        {
            "role": "system",
            "content": f"You are now the following python function: ```# {description}"
            f"\n{function}```\n\nOnly respond with your `return` value.",
        },
        {"role": "user", "content": args},
    ]

    return openai.ChatCompletion.create(model=model, messages=messages, temperature=0)
