from textual.widgets import Static 
from conf.Conf import Conf
from conf.MenuConf import MenuConf
from utils.logger import log
from ui.EListView import EListView

class EMainContainer(Static):
    def __init__(self):
        super().__init__()
        self.conf = None

    async def update_view(self,conf: Conf):
        self.query("*").remove()
        self.conf = conf
        items = await conf.get_items()
        self.elistview = EListView(items)
        self.mount(self.elistview)
        self.refresh()
        self.elistview.focus()

    def go_next(self):
        self.elistview.action_cursor_down()

    def go_previous(self):
        self.elistview.action_cursor_up()

    def get_child(self):
        return self.elistview
 
    def fuzzy_find(self, query: str):
        self.get_child().fuzzy_find(query)

    def fuzzy_filter(self, query: str):
        self.get_child().fuzzy_filter(query)

    def restore_items(self):
        self.get_child().restore_items()

