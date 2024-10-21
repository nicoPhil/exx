import os
import sys
import uuid
import random

try:
    from executor.CommandExecutor import execute_string_command
except ImportError:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    from executor.CommandExecutor import execute_string_command


async def test_simple_command():
    result = await execute_string_command("echo 'hello'")
    assert result.success
    assert result.output == "hello"


async def test_command_with_error():
    result = await execute_string_command("aslkdfjasf", ".")
    assert not result.success
    assert result.error != ""


async def test_command_with_env_vars():
    result = await execute_string_command("echo $HOME", ".")
    assert result.success
    assert result.output == os.environ["HOME"]


async def test_command_with_env_vars_and_quotes():
    result = await execute_string_command('echo "$HOME"', ".")
    assert result.success
    assert result.output == os.environ["HOME"]


async def test_command_with_env_vars_export():
    # setup
    random_uuid = str(uuid.uuid4())
    envvar_key = "TEST_LOCAL"
    if envvar_key in os.environ:
        del os.environ[envvar_key]

    # test
    result = await execute_string_command(f'export {envvar_key}="{random_uuid}"', ".")
    assert result.success
    assert result.output == ""
    assert os.environ[envvar_key] == random_uuid

    # Cleanup
    del os.environ[envvar_key]


async def test_command_with_env_var_write_and_read():
    # setup
    envvar_key = "TEST_LOCAL"
    random_int = str(random.randint(0, 1000000))
    if envvar_key in os.environ:
        del os.environ[envvar_key]

    # test
    result = await execute_string_command(f"export {envvar_key}='{random_int}'", ".")
    assert result.success
    assert result.output == ""
    assert os.environ[envvar_key] == random_int

    result = await execute_string_command(
        f"export {envvar_key}=$(( {random_int} + 1 ))", "."
    )

    assert result.success
    assert result.output == ""
    assert os.environ[envvar_key] == str(int(random_int) + 1)

    # Cleanup
    del os.environ[envvar_key]


async def test_command_with_semicolons():
    result = await execute_string_command("echo 'hello'; echo 'world'")
    assert result.success
    assert result.output == "hello\nworld"


async def test_command_with_semicolons_and_env_vars():
    result = await execute_string_command("echo 'hello'; echo $HOME")
    assert result.success
    assert result.output == f"hello\n{os.environ['HOME']}"


async def test_command_with_newline():
    result = await execute_string_command("echo 'hello\nworld'")
    assert result.success
    assert result.output == "hello\nworld"


async def test_multiline_command():
    result = await execute_string_command("echo 'hello'\necho 'world'")
    assert result.success
    assert result.output == "hello\nworld"


async def test_multiline_with_empty_line():
    result = await execute_string_command("echo 'hello'\n\necho 'world'")
    assert result.success
    assert result.output == "hello\nworld"


async def test_multiline_with_empty_line_at_start():
    result = await execute_string_command("\necho 'hello'\necho 'world'")
    assert result.success
    assert result.output == "hello\nworld"


async def test_multiline_with_empty_line_at_end():
    result = await execute_string_command("echo 'hello'\necho 'world'\n")
    assert result.success
    assert result.output == "hello\nworld"
