import os
import asyncio
import subprocess
from utils.logger import log, log_without_timestamp

_DEBUG_LOG=False

def _debug_log(message):
    if _DEBUG_LOG:
        log(message)

def _debug_log_without_timestamp(message):
    if _DEBUG_LOG:
        log_without_timestamp(message)

async def execute_string_command(command: str, conf_path: str):
    return await execute_string_command_and_source(command, conf_path)

async def execute_string_command_and_source(command: str, conf_path: str):

    _debug_log(f"--Executing command:--")
    _debug_log_without_timestamp(command)
    _debug_log("--")
    # Replace environment variables in the command with their actual values
    command_with_resolved_env_vars = command
    for env_var, value in os.environ.items():
        command_with_resolved_env_vars = command_with_resolved_env_vars.replace(f"${env_var}", value)
        command_with_resolved_env_vars = command_with_resolved_env_vars.replace(f"${{{env_var}}}", value)

    _debug_log(f"--Executing command with resolved environment variables:--")
    _debug_log_without_timestamp(command_with_resolved_env_vars)
    _debug_log("--")

    # If conf_path is a file, get its parent directory
    if os.path.isfile(conf_path):
        conf_path = os.path.dirname(conf_path)
    try:
        # If the command is not multiline, add ; at the end to ensure the command is executed in the same subshell
        if not '\n' in command:
            command = f"{{ {command}; }}"

        script = f"""
        cd {conf_path}
        {{ {command} }}
        echo '---ENV---'
        env
        """

        # Use asyncio to run the command asynchronously
        process = await asyncio.create_subprocess_shell(
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy()
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

        # Split the output into command output and environment variables
        output, _, env_output = stdout.decode().partition('---ENV---')

        # Parse the environment variables
        env_vars = {}
        for line in env_output.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

        # Update the current process's environment
        os.environ.update(env_vars)

        if stderr.decode():
            log(f"Error executing command: {command}. Error: {stderr.decode()}")
            # Log the current working directory
            current_dir = os.getcwd()
            log(f"Current working directory: {current_dir}")
            return {"success": False, "output": stderr.decode(), "error": stderr.decode()}

        return {"success": True, "output": output.strip(), "env_vars": env_vars}
    except subprocess.CalledProcessError as e:
        log(f"Error executing command:")
        log_without_timestamp("---")
        log_without_timestamp(f"{command}")
        log_without_timestamp("---")
        log_without_timestamp(f"Error: {e}")
        log_without_timestamp("---")
        log_without_timestamp(f"Error output: {e.output.decode()}")
        log_without_timestamp("---")
        log_without_timestamp(f"Error stderr: {e.stderr.decode()}")
        log_without_timestamp("---")
        return {"success": False, "output": e.output.decode(), "error": e.stderr.decode()}

async def execute_command(command: dict, conf_path: str):
    if "command" not in command:
        log("Error: 'command' key is missing in the command dictionary")
        raise ValueError("CommandExecutor: command is required")
    if not isinstance(command["command"], str):
        log("Error: 'command' value is not a string")
        raise ValueError("CommandExecutor: command must be a string")

    return await execute_string_command_and_source(command["command"], conf_path)

async def execute_command_and_get_items(command: dict, conf_path: str):
    result = await execute_command(command, conf_path)
    if result["success"]:
        items = result["output"]
        return {"success": True, "items": items, "env_vars": result["env_vars"]}
    else:
        log(f"Error executing command and getting items: {result['error']}")
        return {"success": False, "items": [], "error": result.get("error")}
