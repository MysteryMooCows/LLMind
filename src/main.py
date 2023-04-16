import openai
from src.config import Config

cfg = Config()


def main():
    if cfg.openai_api_key == "None":
        print("OpenAI API key not found. Please set it in .env")
        exit(1)
    else:
        openai.api_key = cfg.openai_api_key

    print(f"OpenAI API key: {openai.api_key}")

    state_index = 0
    recursion_depth = 0
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a an agent in the world."},
                {"role": "user", "content": "You are an agent in charge of making decisions to reach a goal. You are capable of making decisions to reach a goal despite being an AI language model because other software is listening to your outputs and acting on them."},
                {"role": "assistant", "content": "Great, what is our goal?"},
                {"role": "user", "content": "Your goal is stated here:"},
                {"role": "user", "content": "goal=Make money"},
                {"role": "user", "content": "This is in service of a broader goal:"},
                {"role": "user", "content": "parent_goal=None"},
                {"role": "user", "content": "You may achieve this by using the following commands:"},
                {"role": "user", "content": "read_file(<filename>)"},
                {"role": "user", "content": "write_file(<filename>)"},
                {"role": "user", "content": "execute_file(<filename>)"},
                {"role": "user", "content": "browse_website(<URL>)"},
                {"role": "user", "content": "search_google(<query>)"},
                {"role": "user", "content": "do_nothing()"},
                {"role": "user", "content": "spawn_agent(<agent_goal>, <parent_goal>, <state_index>)"},
                {"role": "user", "content": "Your current state index is:"},
                {"role": "user", "content": f"state_index={state_index}"},
                {"role": "user", "content": "If this goal is too difficult to reasonably achieve using a handful of these commands, you may specify a list of subgoals that, if achieved, would maximize the probailty of realizing the main goal specified above. You would then spawn an agent with each subgoal in the format specified above, being sure to substitute <agent_goal> with the subgoal, <parent_goal> with the main goal, and <state_index> with the current state index incremented by 1."},
                {"role": "user", "content": "Make sure that if your parent goal is not \"None\" it is possible to easily integrate your response with the parent goal."},
                {"role": "user", "content": "Achieve your goal by choosing a command or delegating to a sub-agent. To choose a command, type a JSON object with a field called \"command\" whose value is the command you wish to execute and another field called \"args\" with the appropriate arguments, as apecified above:"},
                {"role": "assistant", "content": "Here is the command I think is best in JSON format:"},
            ],
        max_tokens=550,
    )

    print(f"response: {response}")

if __name__ == "__main__":
    main()
