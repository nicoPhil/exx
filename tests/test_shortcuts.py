from helpers import get_listview_children, get_listview_highlighted_child, get_app
from textual.widgets import ListItem, Label

async def test_previous_next():
    async with get_app().run_test() as pilot:
        app = pilot.app
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_0"

        await pilot.press("j")
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_1"
        
        await pilot.press("j")
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_1"

        await pilot.press("k")
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_0"

        await pilot.press("k")
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_0"

async def test_goin():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press("l")
        children = get_listview_children(app)
        assert len(children) == 2
        assert children[0].id == "item_0"
        assert children[1].id == "item_1"
        assert children[0].children[0].renderable.plain == "subfirst-label"
        assert children[1].children[0].renderable.plain == "subsecond-label"

        assert app.main_container.elistview.get_original_id("item_0") == "subfirst"
        assert app.main_container.elistview.get_original_id("item_1") == "subsecond"

async def test_goout():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press("l")
        await pilot.press("h")
        children = get_listview_children(app)
        assert len(children) == 2
        assert children[0].children[0].renderable.plain == "first-label"
        assert children[1].children[0].renderable.plain == "second-label"

