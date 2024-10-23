from executor.CommandExecutor import execute_string_command


async def get_condition_result(command, conf_path: str) -> str:
    result = await execute_string_command(command, conf_path)
    result = result["output"]
    return result


def istrueish(value: str) -> bool:
    return value.lower() in ["true", "yes", "1"]
