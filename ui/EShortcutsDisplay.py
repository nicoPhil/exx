from textual.widgets import Static, Label
from textual.app import ComposeResult
from conf.Conf import Shortcut
from executor.shortcuts_runner import get_condition_result, istrueish


class EShortcutsDisplay(Static):
    def __init__(self):
        super().__init__()
        self.shortcuts = {}

    def compose(self) -> ComposeResult:
        yield Label()

    async def update_view(self, shortcuts: list[Shortcut], conf_path: str):
        self.query("*").remove()
        self.shortcuts = shortcuts
        for shortcut in self.shortcuts:
            if shortcut.is_conditional():
                condition_command = shortcut.get_condition_command()
                condition_result = await get_condition_result(
                    condition_command, conf_path
                )
                if istrueish(condition_result):
                    lbl = Label(f"{shortcut.key}: {shortcut.label}")
            else:
                lbl = Label(f"{shortcut.key}: {shortcut.label}")
            self.mount(lbl)
        self.refresh()
