import openai
import json_parser
from src.config import Config

cfg = Config()

def initialize():
    print("Initialize")

    if cfg.openai_api_key == "None":
        print("OpenAI API key not found. Please set it in .env")
        exit(1)
    else:
        openai.api_key = cfg.openai_api_key

    print(f"OpenAI API key: {openai.api_key}")

    print("Initialize done")

def main():
    print("Main")

    initialize()

    goal = "Write a Python script to print \"Hello world\" to the system console"
    parent_goal = None
    feedback = None
    
    response = openai.ChatCompletion.create(
        model=cfg.model,
        messages=[
                {"role": "system", "content": "You are a an agent in the world."},
                {"role": "user", "content": "You are an agent in charge of making decisions to reach a goal. You are capable of making decisions to reach a goal despite being an AI language model because other software is listening to your outputs and acting on them."},
                {"role": "assistant", "content": "Great, what is our goal?"},
                {"role": "user", "content": "Your goal is stated here:"},
                {"role": "user", "content": f"goal={goal}"},
                {"role": "user", "content": "This goal is an instrumental goal in achieving this higher-order (parent) goal:"},
                {"role": "user", "content": f"parent_goal={parent_goal}"},
                {"role": "user", "content": "You may have been invoked before, since you are designed to achive your goal in incremental steps. Here is some feedback from last invokation, if there is any:"},
                {"role": "user", "content": f"feedback={feedback}"},
                {"role": "user", "content": "You may achieve this by using the following commands:"},
                {"role": "user", "content": "read_file(<filename>)"},
                {"role": "user", "content": "write_file(<filename>)"},
                {"role": "user", "content": "execute_file(<filename>)"},
                {"role": "user", "content": "browse_website(<URL>)"},
                {"role": "user", "content": "search_google(<query>)"},
                {"role": "user", "content": "do_nothing()"},
                {"role": "user", "content": "spawn_agents(<agent_goals_list>, <this_goal>)"},
                {"role": "user", "content": "If this goal is too difficult to reasonably achieve using a single command, you may specify a list of subgoals that, if achieved, would result in the accomplishment of your goal."},
                {"role": "user", "content": "Make sure that if your parent goal is not \"None\" you choose a command that should achieve your goal, or specify a list of subgoals that togethr achieves your goal."},
                {"role": "user", "content": "To use a single command, type a JSON object in the following format:"},
                {"role": "user", "content": json_parser.JSON_SCHEMA["COMMAND"]},
                {"role": "user", "content": "To list subgoals that, if completed, will accomplish your goal, type a JSON object in the following format:"},
                {"role": "user", "content": json_parser.JSON_SCHEMA["SUBGOALS"]},
                {"role": "assistant", "content": "Here is choice I think is best (and why) in the JSON format speciified:"},
            ],
        # max_tokens=1250,
    )

    fixed_response = json_parser.fix_and_parse_json(response.choices[0].message.content)

    with open("log.txt", "w+") as log:
        log.write(f"response:\n{response}")
        log.write(f"fixed_response:\n{fixed_response}")
    
    print("Main done")


if __name__ == "__main__":
    main()
