import os
import sys

try:
    from main import ExecutorApp
except ImportError:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    from main import ExecutorApp


def get_simple_static_conf_dir():
    return os.path.join(os.path.dirname(__file__), "testconfigs", "simplestatic")


def get_lots_of_items_conf_dir():
    return os.path.join(os.path.dirname(__file__), "testconfigs", "staticlotsofitems")


def get_multiline_conf_dir():
    return os.path.join(os.path.dirname(__file__), "testconfigs", "multilines")


def get_listview_children(app: ExecutorApp):
    return app.main_container.elistview.children


def get_listview_highlighted_child(app: ExecutorApp):
    return app.main_container.elistview.highlighted_child


def get_simple_static_conf_app():
    conf_dir = get_simple_static_conf_dir()
    app = ExecutorApp(conf_dir)
    return app


def get_lots_of_items_app():
    conf_dir = get_lots_of_items_conf_dir()
    app = ExecutorApp(conf_dir)
    return app


def get_multiline_conf_app():
    conf_dir = get_multiline_conf_dir()
    app = ExecutorApp(conf_dir)
    return app


def get_last_n_lines_from_console(app: ExecutorApp, n: int):
    retlines = []
    for line in app.econsole.get_lines():
        retlines.append(line.text)

    return retlines[-n:]
