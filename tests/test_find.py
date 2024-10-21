from helpers import (
    get_simple_static_conf_app,
    get_listview_children,
    get_lots_of_items_app,
)
import os


def get_app():
    return get_simple_static_conf_app()


def get_find_key():
    return "f"


def get_filter_key():
    return "F"


def get_down_key():
    return "j"


def get_up_key():
    return "k"


def get_listview_highlighted_child(app):
    return app.main_container.elistview.highlighted_child


async def test_searchbox_is_hidden_by_default():
    async with get_app().run_test() as pilot:
        assert not pilot.app.searchbox.is_visible()


async def test_searchbox_is_visible_after_pressing_slash():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        assert app.searchbox.is_visible()


async def test_searchbox_is_hidden_after_pressing_enter():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        assert pilot.app.searchbox.is_visible()
        await pilot.press("enter")
        assert not pilot.app.searchbox.is_visible()


async def test_searchbox_is_empty_after_pressing_enter_with_value():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await pilot.press("first")
        await pilot.press("enter")
        assert pilot.app.searchbox.value == ""


async def test_searchbox_is_hidden_after_pressing_escape():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        assert pilot.app.searchbox.is_visible()
        await pilot.press("escape")
        assert not pilot.app.searchbox.is_visible()


async def test_searchbox_is_hidden_after_pressing_escape_with_value():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await pilot.press("test")
        await pilot.press("escape")
        assert pilot.app.searchbox.value == ""


async def test_searchbox_find_first_item():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await pilot.press("first")
        assert get_listview_children(pilot.app)[0].highlighted


async def press_word(pilot, word):
    for char in word:
        await pilot.press(char)


async def test_searchbox_find_prioritizes_startswith():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "s")
        assert get_listview_children(pilot.app)[1].highlighted


async def test_searchbox_find_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await press_word(pilot, "second")
        children = get_listview_children(app)
        assert children[1].highlighted


async def test_searchbox_find_updates_selected_id():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "first")
        await pilot.press("enter")
        assert os.environ["SELECTED_ID"] == "first"


async def test_searchbox_find_updates_selected_id_with_second_item():
    async with get_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "second")
        await pilot.press("enter")
        assert os.environ["SELECTED_ID"] == "second"


async def test_searchbox_filter_hides_first_item():
    async with get_app().run_test() as pilot:
        await pilot.press(get_filter_key())
        await press_word(pilot, "first")
        children = get_listview_children(pilot.app)
        assert len(children) == 1
        assert pilot.app.main_container.elistview.children[0].id == "item_0"


async def test_searchbox_filter_hides_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "second")
        children = get_listview_children(app)
        assert len(children) == 1
        assert app.main_container.elistview.children[0].id == "item_1"


async def test_searchbox_filter_highlights_first_item():
    async with get_app().run_test() as pilot:
        await pilot.press(get_filter_key())
        await press_word(pilot, "first")
        assert get_listview_children(pilot.app)[0].highlighted


async def test_searchbox_filter_updates_selected_id_with_second_item():
    async with get_app().run_test() as pilot:
        await pilot.press(get_filter_key())
        await press_word(pilot, "second")
        await pilot.press("enter")
        assert os.environ["SELECTED_ID"] == "second"


async def test_searchbox_filter_restores_items_on_escape():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "first")
        await pilot.press("escape")
        children = get_listview_children(app)
        assert len(children) == 2
        assert app.main_container.elistview.get_original_id("item_0") == "first"
        assert app.main_container.elistview.get_original_id("item_1") == "second"


async def test_searchbox_filter_restores_items_on_backspace():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "fi")
        await pilot.press("backspace")
        await pilot.press("backspace")
        children = get_listview_children(app)
        assert len(children) == 2
        assert app.main_container.elistview.get_original_id("item_0") == "first"
        assert app.main_container.elistview.get_original_id("item_1") == "second"


async def test_searchbox_find_down_cursor_moves_to_next_item_after_search():
    async with get_lots_of_items_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "seventh")
        await pilot.press("enter")
        await pilot.press(get_down_key())
        assert get_listview_highlighted_child(pilot.app).id == "item_7"


async def test_searchbox_find_up_cursor_moves_to_previous_item_after_search():
    async with get_lots_of_items_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "seventh")
        await pilot.press("enter")
        await pilot.press(get_up_key())
        assert get_listview_highlighted_child(pilot.app).id == "item_5"


async def test_searchbox_find_up_cursor_twice_moves_to_previous_item_after_search():
    async with get_lots_of_items_app().run_test() as pilot:
        await pilot.press(get_find_key())
        await press_word(pilot, "seventh")
        await pilot.press("enter")
        await pilot.press(get_up_key())
        await pilot.press(get_up_key())
        assert get_listview_highlighted_child(pilot.app).id == "item_4"
