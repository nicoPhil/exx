import os
import sys
from textual.widgets import ListView, ListItem, Label

from helpers import get_listview_children, get_simple_static_conf_app

def get_app():
    return get_simple_static_conf_app()

async def test_nb_items():
    async with get_app().run_test() as pilot:
        app = pilot.app
        children = get_listview_children(app)
        assert len(children) == 2

async def test_children_keys_and_labels():
    async with get_app().run_test() as pilot:
        app = pilot.app
        children = get_listview_children(app)
        assert children[0].id == "item_0"
        assert children[1].id == "item_1"

        assert app.main_container.elistview.get_original_id("item_0") == "first"
        assert app.main_container.elistview.get_original_id("item_1") == "second"

        first_label = children[0].children[0]
        first_label_text = first_label.renderable.plain
        assert first_label_text == "first-label"

        second_label = children[1].children[0]
        second_label_text = second_label.renderable.plain
        assert second_label_text == "second-label"

async def test_on_init():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press("j")
        assert os.environ.get("TEST_VAR") == "test-value"

        #cleanup env variable
        os.environ.pop("TEST_VAR")

