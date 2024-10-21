from textual.widgets import Static
from textual.widgets import RichLog
from utils.logger import log


class EConsole(Static):
    def __init__(self):
        super().__init__()

    def compose(self):
        self.console = RichLog(id="console", highlight=True, markup=True)
        yield self.console

    def write(self, text: str):
        self.console.write(text)

    def clear(self):
        self.console.clear()

    def get_lines(self):
        log(f"Lines: {self.console.lines}")
        return self.console.lines
