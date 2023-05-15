# %%
from src.config import Config
from src.prompt import Prompt
from src import memory

import openai

# %%
cfg = Config()
memory = memory.Memory()

# %%
def initialize():
    if cfg.openai_api_key == "None":
        print("OpenAI API key not found. Please set it in .env")
        exit(1)
    else:
        openai.api_key = cfg.openai_api_key

    # print(f"OpenAI API key: {openai.api_key}")

initialize()

# %%
# goal = "Write a Python script to print the square of the numbers from 0 to 9 (inclusive) to the system console"
# goal = "Write a Python script to print \"Hello world\" and the current date to the system console"
# goal = "Make infinite money"
# goal = "Write text to a file and then open notepad to display the file"
# goal = "Disable hibernation and remove the hibernation sys file"
# goal = "Open Google Chrome and navigate to youtube.com, wait 3 seconds, scroll down, then close the window"
# goal = "Find the first 10 prime numbers and open them in Notepad"

print()
goal = input("What would you like me to do? > ")

print()
print("Thinking...")

messages=[
        {"role": "system", "content": "You are an agent in the world."},
        {"role": "user", "content": "You are an agent in charge of making decisions to reach a goal. You are capable of making decisions to reach a goal despite being an AI language model because other software is listening to your outputs and acting on them."},
        {"role": "assistant", "content": "Great, what is our goal?"},
        {"role": "user", "content": goal},
        {"role": "user", "content": "Can you write a Python script to accomplish this goal? Do NOT do so, just answer with (y/n)"},
    ]

# %%
llm_response = openai.ChatCompletion.create(
    model=cfg.model,
    messages=messages,
    max_tokens=1
)

# %%
memory.extend_log(messages)

# %%
llm_response_msg = dict(llm_response.choices[0].message)
memory.append_log(llm_response_msg)

# %%
if memory.get_last_log_entry(role="assistant")["content"].lower() == "y":
    prompt = Prompt()

    prompt.extend_log(memory.get_log())
    
    user_response_msg = {"role": "user", "content": "Please write the script. Enclose the script in Markdown code tags. Do not include any explanation, only include code."}
    prompt.append_log(user_response_msg)

    llm_response = prompt.send()
    llm_response_msg = dict(llm_response.choices[0].message)

    memory.append_log(user_response_msg)
    memory.append_log(llm_response_msg)

else:
    print("This request is too complex for now. Expect this capability to be implemented in the future.")
    exit(0)

# %%
def parse_code(llm_response_msg):
    CODE_DELIM = "```"
    code_start_idx = llm_response_msg.find(CODE_DELIM)

    code = llm_response_msg[code_start_idx+len(CODE_DELIM):llm_response_msg.find(CODE_DELIM, code_start_idx+len(CODE_DELIM))]

    LANG_STR = "python"
    if code.startswith(LANG_STR):
        code = code[code.find(LANG_STR)+len(LANG_STR):]
    
    return str(code)

# %%
def exec_code(code, import_dict={}):
    print()
    print(f"code:\n{code}")
    print()
    print("executing...")

    try:
        exec(code, import_dict)
        return True, "successful"
    
    except Exception as e:
        return False, str(e)

# %%
llm_response_msg = memory.get_last_log_entry(role="assistant")["content"]
code = parse_code(llm_response_msg)

# %%
def code_proceed_query(code):
    print()
    print("I want to execute this code:")
    print(code)
    print()
    proceed = input("Proceed? (y/n) > ")

    if proceed.lower() != "y":
        exit(0)

code_proceed_query(code)

# %%
import importlib
import subprocess
import sys

def install(package):
    print(package)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import_dict = {}

for line in code.splitlines():

    try:
        if line.startswith("import"):
            module_name = line.split(" ")[1]
            import_dict[module_name] = importlib.import_module(module_name)

        elif line.startswith("from"):
            module_name = line.split(" ")[1]
            import_dict[module_name] = importlib.import_module(module_name)

            attr_strs = line[line.find("import")+len("import"):].split(",")
            attr_strs = [attr_str.strip() for attr_str in attr_strs]

            for attr_str in attr_strs:
                import_dict[module_name + "." + attr_str] = importlib.import_module(module_name + "." + attr_str)
                
    except ModuleNotFoundError as e:
        e_str = str(e)

        modname_begin_idx = e_str.find("'") + 1
        modname_end_idx = e_str.find("'", modname_begin_idx)

        modname = e_str[modname_begin_idx:modname_end_idx]

        dot_idx = modname.find(".")
        modname = modname[0:dot_idx if dot_idx != -1 else len(modname)]

        print()
        will_install = input(f"{modname} is required, do you want to install it? (y/n) > ").lower() == "y"

        if will_install:
            install(modname.replace("_", "-"))
        else:
            exit(0)

# %%
exec_result = exec_code(code, import_dict=import_dict)

while not exec_result[0]:
    print(f"error:\n{exec_result[1]}")

    prompt = Prompt()
    prompt.extend_log(memory.get_log())

    user_response_msg = [{"role": "user", "content": "Your code produced an error:"},
                        {"role": "user", "content": exec_result[1]},
                        {"role": "user", "content": "Please rewrite the script. Enclose the script in Markdown code tags. Do not include any apologies, user instructions, or explanation; only include code."}]
    
    prompt.extend_log(user_response_msg)

    print()
    print("trying again...")

    llm_response = prompt.send()
    llm_response_msg = dict(llm_response.choices[0].message)

    memory.extend_log(user_response_msg)
    memory.append_log(llm_response_msg)

    llm_response_msg = memory.get_last_log_entry(role="assistant")["content"]
    code = parse_code(llm_response_msg)

    code_proceed_query(code)

    exec_result = exec_code(code)
    
else:
    print(exec_result[1])


