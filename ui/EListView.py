from textual.widgets import ListView, ListItem, Label
from textual.message import Message
from textual.app import ComposeResult
import os
from typing import cast, Optional
from textual.widget import Widget
from rich.text import Text


class EListView(ListView):
    class ItemSelected(Message):
        def __init__(self, item_id: str):
            self.item_id = item_id
            super().__init__()

    def __init__(self, items: list):
        super().__init__()
        self.items = items
        self.item_map: dict[str, str] = {}

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

    def getListItemsFromItems(self):
        list_items = []
        for index, item in enumerate(self.items):
            id = self.get_id_from_item(item)
            value = self.get_value_from_item(item)
            sanitized_value = self._sanitize_value(value)
            sanitized_id = f"item_{index}"
            self.item_map[sanitized_id] = id
            list_items.append(ListItem(Label(sanitized_value), id=sanitized_id))
        return list_items

    def compose(self) -> ComposeResult:
        for li in self.getListItemsFromItems():
            yield li

    def get_original_id(self, item_id):
        return self.item_map[item_id]

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event and event.item:
            self.on_highlighted(event.item.id)

    def on_highlighted(self, id) -> None:
        original_id = self.get_original_id(id)
        os.environ["SELECTED_ID"] = original_id
        self.post_message(self.ItemSelected(original_id))

    def _get_label_value(self, li: ListItem) -> str:
        first_child_widget: Widget
        label: Label
        first_child_widget = li.children[0]
        label = cast(Label, first_child_widget)
        renderable = label.renderable
        if isinstance(renderable, Text):
            return renderable.plain
        else:
            raise ValueError(
                f"Label value is not a string,it is of type {type(renderable)} "
            )

    def get_first_matching_item(self, query: str) -> Optional[ListItem]:
        # First pass: check if query is a prefix of the label
        for li in cast(list[ListItem], self.children):
            label_value = self._get_label_value(li)
            if label_value.lower().startswith(query.lower()):
                return li

        # Second pass: check if query is contained within the label
        for li in cast(list[ListItem], self.children):
            label_value = self._get_label_value(li)
            if query.lower() in label_value.lower():
                return li

        return None

    def scroll_and_highlight(self, li: ListItem):
        if not li:
            return
        self.scroll_to_widget(li)
        self.on_highlighted(li.id)

    async def fuzzy_filter(self, query: str):
        await self.restore_items()
        items_to_remove = []
        for li in cast(list[ListItem], self.children):
            label_value = self._get_label_value(li)

            if query.lower() not in label_value.lower():
                items_to_remove.append(li)

        items_to_remove_indices = [self.children.index(li) for li in items_to_remove]
        await self.remove_items(items_to_remove_indices)

        if self.children:
            first_item = cast(ListItem, self.children[0])
            self.index = 0
            self.scroll_and_highlight(first_item)

    async def fuzzy_find(self, query: str):
        matched_item = self.get_first_matching_item(query)
        if not matched_item:
            return

        for li in cast(list[ListItem], self.children):
            li.highlighted = False

        matched_item.highlighted = True
        self.index = self.children.index(matched_item)
        self.scroll_and_highlight(matched_item)

    async def restore_items(self):
        await self.clear()
        for li in self.getListItemsFromItems():
            await self.append(li)
