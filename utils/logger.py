import io
from datetime import datetime

def log(message: str):
    with open('log.log', 'a') as log_file:
        current_time = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{current_time}] {message}"
        log_file.write(log_entry + '\n')

def log_without_timestamp(message: str):
    with open('log.log', 'a') as log_file:
        log_file.write(message + '\n')
