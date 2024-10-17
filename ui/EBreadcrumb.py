from textual.widgets import Static, Label

class EBreadcrumb(Static):
    def __init__(self):
        super().__init__()
        self.items = []
        self.breadcrumb = Label(id="breadcrumb")

    def compose(self):
        yield self.breadcrumb

    def _change_text(self, text: str):
        self.breadcrumb.update(text)

    def _update_text(self):
        text = "/".join(self.items)
        self._change_text(text)

    def push_item(self, item: str):
        self.items.append(item)
        self._update_text()

    def pop_item(self):
        if len(self.items) == 0:
            return
        self.items.pop()
        self._update_text()


