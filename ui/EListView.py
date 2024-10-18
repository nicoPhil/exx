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
        self.on_highlighted(event.item.id)

    def on_highlighted(self, id) -> None:
        original_id = self.get_original_id(id)
        os.environ["SELECTED_ID"] = original_id
        self.post_message(self.ItemSelected(original_id))

    def get_first_matching_item(self, query: str) -> ListItem:
        for li in self.children:
            label = li.children[0].renderable
            label_value = label.plain

            if label_value.lower().startswith(query.lower()):
                self.scroll_to_widget(li)
                return li

        for li in self.children:
            label = li.children[0].renderable
            label_value = label.plain
            if query.lower() in label_value.lower():
                return li

        return None

    def fuzzy_filter(self, query: str):
        for li in self.children:
            label = li.children[0].renderable
            label_value = label.plain
            if not query.lower() in label_value.lower():
                li.styles.display = "none"
            else:
                li.styles.display = "block"

        # Find the first visible item
        first_visible_item = next((li for li in self.children if li.styles.display == "block"), None)
        if first_visible_item:
            first_visible_item.highlighted = True
            self.scroll_to_widget(first_visible_item)
            self.on_highlighted(first_visible_item.id)


    def fuzzy_find(self, query: str):
        matched_item = self.get_first_matching_item(query)
        if not matched_item:
            return

        for li in self.children:
            li.highlighted=False

        matched_item.highlighted=True
        self.scroll_to_widget(matched_item)
        self.on_highlighted(matched_item.id)

    def restore_items(self):
        for li in self.children: li.styles.display = "block"



