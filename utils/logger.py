import inspect
from datetime import datetime


def log(message: str):
    caller = inspect.stack()[1].function  # Get the calling function's name
    with open("log.log", "a") as log_file:
        current_time = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{current_time}] [{caller}] {message}"
        log_file.write(log_entry + "\n")


def log_without_timestamp(message: str):
    caller = inspect.stack()[1].function  # Get the calling function's name
    with open("log.log", "a") as log_file:
        log_file.write(f"[{caller}] {message}\n")
