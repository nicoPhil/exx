from executor.CommandExecutor import execute_string_command


def is_conditional_shortcut(shortcut):
    return "condition" in shortcut and "command" in shortcut["condition"]


def get_conditional_shortcut_command(shortcut):
    return shortcut["condition"]["command"]


async def get_condition_result(command, conf_path: str):
    result = await execute_string_command(command, conf_path)
    result = result["output"]
    return result


def istrueish(value: str):
    return value.lower() in ["true", "yes", "1"]
