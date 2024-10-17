from textual.widgets import ListView, ListItem, Label
from textual.message import Message
from textual.app import ComposeResult
from utils.logger import log
import os

class EListView(ListView):
    class ItemSelected(Message):
        def __init__(self, item_id: str):
            self.item_id = item_id
            super().__init__()

    def __init__(self, items: list):
        super().__init__()
        self.items = items
        self.item_map = {}  

    def get_id_from_item(self, item):
        if isinstance(item, dict):
            if "id" in item:
                return item["id"]
            elif "key" in item:
                return item["key"]
            else:
                raise ValueError("Item does not have an id or key")
        else:
            return item
    
    def get_value_from_item(self, item):
        if isinstance(item, dict):
            if "values" in item:
                return item["values"]
            elif "label" in item:
                return item["label"]
            else:
                raise ValueError("Item does not have a value or label")
        else:
            return item

    def _sanitize_value(self, value):
        return value.replace("\t", " ").replace("\n", " ")
        
    def compose(self) -> ComposeResult:
        for index, item in enumerate(self.items):
            id = self.get_id_from_item(item)
            value = self.get_value_from_item(item)
            sanitized_value = self._sanitize_value(value)
            sanitized_id = f"item_{index}"
            self.item_map[sanitized_id] = id
            yield ListItem(Label(sanitized_value), id=sanitized_id)

    def get_original_id(self, item_id):
        return self.item_map[item_id]

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        original_id = self.get_original_id(event.item.id)
        os.environ["SELECTED_ID"] = original_id
        self.post_message(self.ItemSelected(original_id))
