import openai
from src.config import Config

cfg = Config()


def main():
    if cfg.openai_api_key == "None":
        print("OpenAI API key not found. Please set it in .env")
        exit(1)
    else:
        openai.api_key = cfg.openai_api_key

    print(openai.api_key)


if __name__ == "__main__":
    main()
