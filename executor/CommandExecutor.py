import os
import asyncio
import subprocess
from dataclasses import dataclass
from utils.logger import log, log_without_timestamp

_DEBUG_LOG = False

ENV_SEPARATOR = "---ENV---"


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
    log_without_timestamp(f"Error output: {e.output}")
    log_without_timestamp("---")
    log_without_timestamp(f"Error stderr: {e.stderr}")
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
        echo '{ENV_SEPARATOR}'
        env
        """
    return script


def _restore_env_vars(env_output: str):
    env_vars = {}
    for line in env_output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env_vars[key] = value
    os.environ.update(env_vars)


async def execute_string_command(
    command: str,
    conf_path: str = ".",
    stdout_callback=None,
    stderr_callback=None,
):
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

        # Lists to store the full output
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        env_output_lines: list[str] = []  # For capturing environment variables

        async def read_stream(stream, callback, output_list):
            is_env_section = False  # Initialize here

            while True:
                line = await stream.readline()
                if line:
                    decoded_line = line.decode().strip()

                    if decoded_line == ENV_SEPARATOR:
                        is_env_section = True  # Switch to capturing environment output
                        continue  # Skip this line

                    if is_env_section:
                        env_output_lines.append(decoded_line)  # Store env lines
                    else:
                        output_list.append(
                            decoded_line
                        )  # Store the line for later return

                    if not is_env_section and callback:
                        callback(decoded_line)  # Use provided callback
                else:
                    break

        # Use the provided callbacks or default to printing
        await asyncio.gather(
            read_stream(process.stdout, stdout_callback, stdout_lines),
            read_stream(process.stderr, stderr_callback, stderr_lines),
        )

        # Wait for the process to finish
        await process.wait()

        # Check for a non-zero return code
        if (process.returncode is not None and process.returncode != 0) or stderr_lines:
            if process.returncode is None:
                return_code = 0
            else:
                return_code = process.returncode

            raise subprocess.CalledProcessError(
                return_code,
                command,
                output="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
            )

        # Combine the stdout lines into one output
        output = "\n".join(stdout_lines)

        # Restore environment variables from env_output_lines
        if env_output_lines:
            _restore_env_vars("\n".join(env_output_lines))

        return CommandExecutorResult(success=True, output=output.strip(), error="")
    except subprocess.CalledProcessError as e:
        _log_error(command, e)
        return CommandExecutorResult(
            success=False,
            output=e.output.strip(),  # Ensure we strip any unnecessary whitespace
            error=e.stderr.strip(),  # Same here for error output
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
