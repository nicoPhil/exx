import os
from typing import List

from helpers import (
    get_listview_children,
    get_listview_highlighted_child,
    get_simple_static_conf_app,
    get_shortcut_dict_conf_app,
    get_last_n_lines_from_console,
)


def get_app():
    return get_simple_static_conf_app()

def get_app_shortcut_dict():
    return get_shortcut_dict_conf_app()

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


async def test_shortcut_action_command():
    async with get_app().run_test() as pilot:
        await pilot.press("a")
        assert os.environ.get("TEST_VAR_A_TEST") == "test-value-a-test"

        await pilot.press("b")
        assert os.environ.get("TEST_VAR_B_TEST") == "test-value-a-test"

        # cleanup env variable
        os.environ.pop("TEST_VAR_A_TEST")
        os.environ.pop("TEST_VAR_B_TEST")


async def test_shortcut_action_command_multiline_results():
    app = get_app()
    async with app.run_test() as pilot:
        await pilot.press("c")
        expected_lines: List[str] = []
        expected_lines.append("hello")
        expected_lines.append("world")
        expected_lines.append("third")
        expected_lines.append("fourth")
        # Get the last n lines from the console
        last_n_lines = get_last_n_lines_from_console(app, len(expected_lines) + 1)
        assert last_n_lines[:-1] == expected_lines


async def test_shortcut_inherit():
    app = get_app()
    async with app.run_test() as pilot:
        await pilot.press("l")
        children = get_listview_children(pilot.app)
        assert len(children) == 2

        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_0"

        await pilot.press("j")
        children = get_listview_children(pilot.app)
        assert len(children) == 2
        highlighted_child = get_listview_highlighted_child(app)
        assert highlighted_child.id == "item_1"

async def test_shortcut_as_dict():
    app = get_app_shortcut_dict()
    async with app.run_test() as pilot:
        await pilot.press("a")
        assert os.environ.get("TEST_VAR_A_TEST") == "test-value-a-test"
        await pilot.press("b")
        assert os.environ.get("TEST_VAR_B_TEST") == "test-value-b-test"
        await pilot.press("c")
        assert os.environ.get("TEST_VAR_C_TEST") == "test-value-c-test"
