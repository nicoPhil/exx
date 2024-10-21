import os
import asyncio
import subprocess
from dataclasses import dataclass
from utils.logger import log, log_without_timestamp

_DEBUG_LOG = True


@dataclass(frozen=True)
class CommandExecutorResult:
    success: bool
    output: str
    error: str


def _debug_log(message):
    if _DEBUG_LOG:
        log(message)


def _debug_log_without_timestamp(message):
    if _DEBUG_LOG:
        log_without_timestamp(message)

def _debug_log_command(command: str):
    _debug_log("--Executing command:--")
    _debug_log_without_timestamp(command)
    _debug_log("--")
    _debug_log_command_with_resolved_env_vars(command)


def _debug_log_command_with_resolved_env_vars(command: str):

    command_with_resolved_env_vars = command
    for env_var, value in os.environ.items():
        command_with_resolved_env_vars = command_with_resolved_env_vars.replace(
            f"${env_var}", value
        )
        command_with_resolved_env_vars = command_with_resolved_env_vars.replace(
            f"${{{env_var}}}", value
        )
    _debug_log("--with resolved environment variables:--")
    _debug_log_without_timestamp(command_with_resolved_env_vars)
    _debug_log("--")

def _log_error(command: str, e: subprocess.CalledProcessError):
    log("Error executing command:")
    log_without_timestamp("---")
    log_without_timestamp(f"{command}")
    log_without_timestamp("---")
    log_without_timestamp(f"Error: {e}")
    log_without_timestamp("---")
    log_without_timestamp(f"Error output: {e.output.decode()}")
    log_without_timestamp("---")
    log_without_timestamp(f"Error stderr: {e.stderr.decode()}")
    log_without_timestamp("---")

def _get_conf_path_dir(conf_path: str):
    # If conf_path is a file, get its parent directory
    if os.path.isfile(conf_path):
        return os.path.dirname(conf_path)
    return conf_path

def _pimp_command(command: str, conf_path: str):
    # If the command is not multiline, add ; at the end to ensure the command is executed in the same subshell
    if "\n" not in command:
        command = f"{{ {command}; }}"

    script = f"""
        cd {conf_path}
        {command} 
        echo '---ENV---'
        env
        """
    return script


def _resolve_env_vars(env_output: str):
    env_vars = {}
    for line in env_output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env_vars[key] = value
    os.environ.update(env_vars)

async def execute_string_command(command: str, conf_path: str = "."):
    _debug_log_command(command)

    conf_path = _get_conf_path_dir(conf_path)
    script = _pimp_command(command, conf_path)
    try:
        # Use asyncio to run the command asynchronously
        process = await asyncio.create_subprocess_shell(
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return_code: int
            if not process.returncode:
                return_code = -1
            else:
                return_code = process.returncode
            raise subprocess.CalledProcessError(
                return_code, command, output=stdout, stderr=stderr
            )

        # Split the output into command output and environment variables
        output, _, env_output = stdout.decode().partition("---ENV---")
        _resolve_env_vars(env_output)

        if stderr.decode():
            log(f"Error executing command: {command}. Error: {stderr.decode()}")
            # Log the current working directory
            current_dir = os.getcwd()
            log(f"Current working directory: {current_dir}")
            return CommandExecutorResult(
                success=False,
                output=stderr.decode(),
                error=stderr.decode(),
            )

        return CommandExecutorResult(
            success=True,
            output=output.strip(),
            error="",
        )
    except subprocess.CalledProcessError as e:
        _log_error(command, e)
        return CommandExecutorResult(
            success=False,
            output=e.output.decode(),
            error=e.stderr.decode(),
        )


async def execute_command(command: dict, conf_path: str):
    if "command" not in command:
        log("Error: 'command' key is missing in the command dictionary")
        raise ValueError("CommandExecutor: command is required")
    if not isinstance(command["command"], str):
        log("Error: 'command' value is not a string")
        raise ValueError("CommandExecutor: command must be a string")

    return await execute_string_command(command["command"], conf_path)


async def execute_command_and_get_items(command: dict, conf_path: str):
    result = await execute_command(command, conf_path)
    if result.success:
        items = result.output
        return CommandExecutorResult(
            success=True,
            output=items,
            error="",
        )
    else:
        log(f"Error executing command and getting items: {result.error}")
        return CommandExecutorResult(
            success=False,
            output="",
            error=result.error,
        )
