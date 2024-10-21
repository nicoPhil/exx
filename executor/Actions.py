from executor.CommandExecutor import execute_string_command


async def run_action(action, conf_path):
    if not isinstance(action, dict):
        raise ValueError("Action: must be a dictionary")
    if "command" not in action:
        raise ValueError("Action: must contain command")

    command = action["command"]
    if not isinstance(command, str):
        raise ValueError("Action: command must be a string")

    result = await execute_string_command(command, conf_path)
    output = result.output

    if "output" in action:
        output_type = action["output"]
        if output_type == "console":
            return output
        else:
            raise ValueError(f"Action: unknown output type: {output_type}")
    return output
