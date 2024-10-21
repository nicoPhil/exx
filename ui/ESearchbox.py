from textual.widgets import Input
from textual.message import Message


class ESearchbox(Input):
    class MyChanged(Message):
        def __init__(self, value: str):
            self.value = value
            super().__init__()

    class MyEscape(Message):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.mode = "find"

    def is_visible(self):
        return self.styles.display != "none"

    def get_escape_key(self):
        return "escape"

    def get_enter_key(self):
        return "enter"

    def on_key(self, event):
        if event.key == self.get_escape_key():
            self.on_escape()
        if event.key == self.get_enter_key():
            self.hide()

    def on_escape(self):
        self.hide()
        self.post_message(ESearchbox.MyEscape())

    def _show(self):
        self.styles.display = "block"
        self.focus()

    def show_mode_find(self):
        self._show()
        self.mode = "find"

    def show_mode_filter(self):
        self._show()
        self.mode = "filter"

    def get_mode(self):
        return self.mode

    def hide(self):
        self.styles.display = "none"
        self.value = ""
        self.blur()

    def on_input_changed(self, event: Input.Changed) -> None:
        if not self.is_visible():
            return

        val = self.value
        changed = ESearchbox.MyChanged(val)
        self.post_message(changed)
