import json
import re
from typing import Any, Dict, Optional, Union

from call_ai_function import call_ai_function
import config

cfg = config.Config()


JSON_SCHEMA ={"COMMAND": """
{
    "command": {
        "name": "command name",
        "args": {
            "arg name": "value"
        }
    },
    "thoughts":
    {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    }
}
""", 

"SUBGOALS": """
{
    "subgoals": {
        1: "first_subgoal":
            {
                "purpose": "how this subgoal helps accomplish your current goal"}
            },
        2: "second_subgoal":
            {
                "purpose": "how this subgoal helps accomplish your current goal"}
            },
        n: "nth_subgoal":
            {
                "purpose": "how this subgoal helps accomplish your current goal"}
            },
    },
    "thoughts":
    {
        "text": "thought",
        "reasoning": "reasoning",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    }
}
"""}

# TODO: implement
def jsonrepair_wrapper(json_str: str) -> Union[str, Dict[Any, Any]]:
    pass


def fix_and_parse_json(json_str: str, try_to_fix_with_gpt: bool=True) -> Union[str, Dict[Any, Any]]:
    """Fix and parse JSON string"""
    try:
        json_str = json_str.replace("\t", "")
        return json.loads(json_str)
    except json.JSONDecodeError as _:  # noqa: F841
        try:
            json_str = correct_json(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as _:  # noqa: F841
            pass

    # Let's do something manually:
    # sometimes GPT responds with something BEFORE the braces:
    # "I'm sorry, I don't understand. Please try again."
    # {"text": "I'm sorry, I don't understand. Please try again.",
    #  "confidence": 0.0}
    # So let's try to find the first brace and then parse the rest
    #  of the string
    try:
        brace_index = json_str.index("{")
        json_str = json_str[brace_index:]
        last_brace_index = json_str.rindex("}")
        json_str = json_str[: last_brace_index + 1]
        return json.loads(json_str)
    
    # Can throw a ValueError if there is no "{" or "}" in the json_str
    except (json.JSONDecodeError, ValueError) as e:  # noqa: F841
        if try_to_fix_with_gpt:
            print(
                "Warning: Failed to parse AI output, attempting to fix."
                "\n If you see this warning frequently, it's likely that"
                " your prompt is confusing the AI. Try changing it up"
                " slightly."
            )

            # Now try to fix this up using the ai_functions
            ai_fixed_json = fix_json_GPT(json_str, JSON_SCHEMA_COMMAND)

            if ai_fixed_json != "failed":
                return json.loads(ai_fixed_json)
            else:
                # This allows the AI to react to the error message,
                #   which usually results in it correcting its ways.
                print("Failed to fix AI output, telling the AI.")
                return json_str
        else:
            raise e
        

def fix_json_GPT(json_str: str, schema: str) -> str:
    """Fix the given JSON string to make it parseable and fully compliant with the provided schema."""

    # Try to fix the JSON using GPT:
    function_string = "def fix_json(json_str: str, schema:str=None) -> str:"
    args = [f"'''{json_str}'''", f"'''{schema}'''"]
    description_string = (
        "Fixes the provided JSON string to make it parseable"
        " and fully compliant with the provided schema.\n If an object or"
        " field specified in the schema isn't contained within the correct"
        " JSON, it is omitted.\n This function is brilliant at guessing"
        " when the format is incorrect."
    )

    # If it doesn't already start with a "`", add one:
    if not json_str.startswith("`"):
        json_str = "```json\n" + json_str + "\n```"
    result_string = call_ai_function(
        function_string, args, description_string, model=cfg.model
    )

    print("------------ JSON FIX ATTEMPT ---------------")
    print(f"Original JSON: {json_str}")
    print("-----------")
    print(f"Fixed JSON: {result_string}")
    print("----------- END OF FIX ATTEMPT ----------------")

    try:
        json.loads(result_string)  # just check the validity
        return result_string
    except:
        return "failed"
    

def correct_json(json_str: str) -> str:
    """
    Correct common JSON errors.

    Args:
        json_str (str): The JSON string.
    """

    try:
        if cfg.debug_mode:
            print("json", json_str)
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError as e:
        if cfg.debug_mode:
            print("json loads error", e)
        error_message = str(e)
        if error_message.startswith("Invalid \\escape"):
            json_str = fix_invalid_escape(json_str, error_message)
        if error_message.startswith(
            "Expecting property name enclosed in double quotes"
        ):
            json_str = add_quotes_to_property_names(json_str)
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError as e:
                if cfg.debug_mode:
                    print("json loads error - add quotes", e)
                error_message = str(e)
        if balanced_str := balance_braces(json_str):
            return balanced_str
    return json_str


def extract_char_position(error_message: str) -> int:
    """Extract the character position from the JSONDecodeError message.

    Args:
        error_message (str): The error message from the JSONDecodeError
          exception.

    Returns:
        int: The character position.
    """
    import re

    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")


def add_quotes_to_property_names(json_string: str) -> str:
    """
    Add quotes to property names in a JSON string.

    Args:
        json_string (str): The JSON string.

    Returns:
        str: The JSON string with quotes added to property names.
    """

    def replace_func(match):
        return f'"{match.group(1)}":'

    property_name_pattern = re.compile(r"(\w+):")
    corrected_json_string = property_name_pattern.sub(replace_func, json_string)

    try:
        json.loads(corrected_json_string)
        return corrected_json_string
    except json.JSONDecodeError as e:
        raise e


def balance_braces(json_string: str) -> Optional[str]:
    """
    Balance the braces in a JSON string.

    Args:
        json_string (str): The JSON string.

    Returns:
        str: The JSON string with braces balanced.
    """

    open_braces_count = json_string.count("{")
    close_braces_count = json_string.count("}")

    while open_braces_count > close_braces_count:
        json_string += "}"
        close_braces_count += 1

    while close_braces_count > open_braces_count:
        json_string = json_string.rstrip("}")
        close_braces_count -= 1

    try:
        json.loads(json_string)
        return json_string
    except json.JSONDecodeError:
        pass

def fix_invalid_escape(json_str: str, error_message: str) -> str:
    while error_message.startswith("Invalid \\escape"):
        bad_escape_location = extract_char_position(error_message)
        json_str = json_str[:bad_escape_location] + json_str[bad_escape_location + 1 :]
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            if cfg.debug_mode:
                print("json loads error - fix invalid escape", e)
            error_message = str(e)
    return json_str
