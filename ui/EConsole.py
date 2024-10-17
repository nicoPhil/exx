from textual.widgets import Static, Button
from textual.message import Message
from textual.widgets import RichLog

class EConsole(Static):
    def __init__(self):
        super().__init__()

    def compose(self):
        self.console = RichLog(id="console",highlight=True,markup=True)
        yield self.console

    def write(self, text: str):
        self.console.write(text)

    def clear(self):
        self.console.clear()