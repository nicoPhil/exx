from textual.widgets import Static, Label
from textual.app import ComposeResult
from utils.logger import log
from executor.CommandExecutor import execute_command_and_get_items, execute_string_command
from executor.shortcuts import is_conditional_shortcut, get_conditional_shortcut_command, get_condition_result, istrueish

class EShortcutsDisplay(Static):
    def __init__(self):
        super().__init__()
        self.shortcuts = {}

    def compose(self) -> ComposeResult:
        yield Label()

    async def update_view(self, shortcuts: dict,conf_path: str):
        self.query("*").remove()
        self.shortcuts = shortcuts
        for shortcut in self.shortcuts:
            is_conditional = is_conditional_shortcut(shortcut)
            if is_conditional:
                condition_command = get_conditional_shortcut_command(shortcut)
                condition_result = await get_condition_result(condition_command,conf_path)
                if istrueish(condition_result):
                    lbl = Label(f"{shortcut['key']}: {shortcut['label']}")
            else:
                lbl = Label(f"{shortcut['key']}: {shortcut['label']}")
            self.mount(lbl)
        self.refresh()
