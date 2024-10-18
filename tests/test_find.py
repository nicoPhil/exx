from helpers import  get_simple_static_conf_app, get_listview_children
import pytest
import os
def get_app():
    return get_simple_static_conf_app()

def get_find_key():
    return "f"

def get_filter_key():
    return "F"


async def test_searchbox_is_hidden_by_default():
    async with get_app().run_test() as pilot:
        app = pilot.app
        assert app.searchbox.is_visible() == False

async def test_searchbox_is_visible_after_pressing_slash():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        assert app.searchbox.is_visible() == True


async def test_searchbox_is_hidden_after_pressing_enter():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        assert app.searchbox.is_visible() == True
        await pilot.press("enter")
        assert app.searchbox.is_visible() == False

async def test_searchbox_is_empty_after_pressing_enter_with_value():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await pilot.press("first")
        await pilot.press("enter")
        assert app.searchbox.value == ""

async def test_searchbox_is_hidden_after_pressing_escape():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        assert app.searchbox.is_visible() == True
        await pilot.press("escape")
        assert app.searchbox.is_visible() == False

async def test_searchbox_is_hidden_after_pressing_escape_with_value():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await pilot.press("test")
        await pilot.press("escape")
        assert app.searchbox.value == ""

async def test_searchbox_find_first_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await pilot.press("first")
        children = get_listview_children(app)
        assert children[0].highlighted == True


async def press_word(pilot, word):
    for char in word:
        await pilot.press(char)

async def test_searchbox_find_prioritizes_startswith():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await press_word(pilot, "s")
        children = get_listview_children(app)
        assert children[1].highlighted == True

async def test_searchbox_find_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await press_word(pilot, "second")
        children = get_listview_children(app)
        assert children[1].highlighted == True
        
async def test_searchbox_find_updates_selected_id():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await press_word(pilot, "first")
        await pilot.press("enter")
        assert os.environ["SELECTED_ID"] == "first"

async def test_searchbox_find_updates_selected_id_with_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_find_key())
        await press_word(pilot, "second")
        await pilot.press("enter")
        assert os.environ["SELECTED_ID"] == "second"

async def test_searchbox_filter_hides_first_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "first")
        children = get_listview_children(app)
        assert children[0].styles.display == "block"
        assert children[1].styles.display == "none"

async def test_searchbox_filter_hides_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "second")
        children = get_listview_children(app)
        assert children[0].styles.display == "none"
        assert children[1].styles.display == "block"

async def test_searchbox_filter_highlights_first_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
        await pilot.press(get_filter_key())
        await press_word(pilot, "first")
        children = get_listview_children(app)
        assert children[0].highlighted == True
        assert children[1].highlighted == False

async def test_searchbox_filter_updates_selected_id_with_second_item():
    async with get_app().run_test() as pilot:
        app = pilot.app
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
        assert children[0].styles.display == "block"
        assert children[1].styles.display == "block"
