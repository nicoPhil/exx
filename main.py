import os
import sys
from conf.ConfLoader import ConfLoader
from textual.app import App, ComposeResult
from textual.widgets import ListView, Button, LoadingIndicator,Label
from ui.EListView import EListView
from ui.EConsole import EConsole
from ui.EMainContainer import EMainContainer
from utils.logger import log
from ui.EShortcutsDisplay import EShortcutsDisplay
from conf.Conf import Conf
from conf.ConfStack import ConfStack
from executor.Actions import run_action
from ui.EBreadcrumb import EBreadcrumb
from textual.worker import Worker, WorkerState
from textual.containers import Horizontal, VerticalScroll
import pyperclip
import asyncio
from executor.shortcuts import is_conditional_shortcut, get_conditional_shortcut_command, get_condition_result, istrueish

class ExecutorApp(App):

    def __init__(self, conf_root_path: str = None):
        
        if conf_root_path is None:
            self.conf_root_path = os.getcwd()
        else:
            print("conf_root_path is not None")
            if not os.path.exists(conf_root_path):
                raise FileNotFoundError(f"Configuration file not found: {conf_root_path}")
            self.conf_root_path = conf_root_path  # Add this line

        self.conf_loader = ConfLoader(self.conf_root_path)  # Use self.conf_root_path here
        self.conf_stack = ConfStack()
        super().__init__()

    def setup_layout(self):
        self.main_container.styles.border = ("round", "white")
        self.main_container.styles.height = "1fr"
        self.main_container.styles.width = "1fr"

        self.shortcuts_display.styles.width = "0.4fr"

        self.econsole.styles.height = "1fr"
        self.econsole.styles.border = ("round", "white")
        
    def compose(self) -> ComposeResult:
        self.main_container = EMainContainer()
        self.econsole = EConsole()
        self.shortcuts_display = EShortcutsDisplay()
        self.breadcrumb = EBreadcrumb()
        yield VerticalScroll(
            self.breadcrumb,
            Horizontal(
                self.main_container,
                self.shortcuts_display
            ),
            Label("Console:"),
            self.econsole,
        )

    async def load_conf(self, conf_path):
        conf = await self.conf_loader.load_conf(conf_path)
        await self.restore_conf(conf)
        return conf

    async def restore_conf(self,conf: Conf):
        self.run_worker(self.main_container.update_view(conf), exclusive=True)
        await self.shortcuts_display.update_view(conf.get_shortcuts(),conf.conf_path)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.RUNNING:
            self.main_container.loading = True
        elif event.state == WorkerState.SUCCESS:
            self.main_container.loading = False


    def get_current_conf_label(self):
        if "SELECTED_ID" in os.environ:
            return os.environ["SELECTED_ID"]
        else:
            return ""

    def push_conf(self, conf: Conf):
        self.breadcrumb.push_item(self.get_current_conf_label())
        self.conf_stack.push(conf)

    def pop_conf(self):
        self.breadcrumb.pop_item()
        self.conf_stack.pop()

    async def timer_check_conf_modification(self):
        while True:
            await asyncio.sleep(1)
            await self.reload_conf_if_needed()

    async def on_mount(self) -> None:
        new_conf = await self.load_conf(self.conf_loader.get_conf_root_dir())
        self.push_conf(new_conf)
        self.setup_layout()
        asyncio.create_task(self.timer_check_conf_modification())

    def get_env_vars(self):
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith("EEX_"):
                env_vars[key] = value
        return env_vars

    def get_current_conf(self):
        return self.conf_stack.top()

    async def on_shortcut(self, key):
        shortcut = self.get_current_conf().get_shortcut(key)
        if shortcut is None:
            return

        if is_conditional_shortcut(shortcut):
            condition_command = get_conditional_shortcut_command(shortcut)
            condition_result = await get_condition_result(condition_command,self.get_current_conf().conf_path)
            if not istrueish(condition_result):
                return

        if "action" in shortcut:
            action = shortcut["action"]
            if action == "goin":
                await self.on_goin()
            elif action == "goout":
                await self.on_goout()
            elif action == "next":
                self.on_next()
            elif action == "previous":
                self.on_previous()
            elif action == "refresh":
                await self.on_refresh()
            elif action == "clear_console":
                self.on_clear_console()
            elif action == "yankid" or action == "copyid":
                self.on_yankid()
            else:
                log = await run_action(action,self.get_current_conf().conf_path)
                if log:
                    self.econsole.write("---- ACTION OUTPUT ----")
                    self.econsole.write(log)

    async def on_key(self, event):
        if self.get_current_conf().is_shortcut(event.key):
            await self.on_shortcut(event.key)
            return

        if event.key == "q":
            self.exit()
        if event.key == "e":
            self.econsole.write(self.get_env_vars())
        if event.key == "h":
            await self.on_goout()

    def on_next(self):
        self.main_container.go_next()

    def on_previous(self):
        self.main_container.go_previous()

    async def on_goin(self):
        selected_id = os.environ["SELECTED_ID"]
        mconf = self.get_current_conf()
        await mconf.on_goin()
        goin_id = mconf.get_goin_id(selected_id)
        goin_path = self.conf_loader.get_goin_path(mconf.conf_path, goin_id)
        new_conf = await self.load_conf(goin_path)
        self.push_conf(new_conf)

    async def on_goout(self):
        log("on_goout")
        mconf = self.get_current_conf()
        await mconf.on_goout()
        if not self.conf_stack.only_one():
            self.pop_conf()
        new_conf = self.conf_stack.top()
        await self.reload_conf_if_needed()

        await self.restore_conf(new_conf)

    async def reload_conf_if_needed(self):
        new_conf = self.get_current_conf()
        if new_conf.is_conf_obsolete():
            self.write_to_console(f"Obsolete conf detected: {new_conf.conf_path}")
            new_conf = await self.load_conf(new_conf.conf_path)
            self.conf_stack.pop()
            self.conf_stack.push(new_conf)
            self.write_to_console("Reloaded new conf")

    async def on_refresh(self):
        await self.reload_conf_if_needed()
        self.restore_conf(self.get_current_conf())

    def on_clear_console(self):
        self.econsole.clear()

    def write_to_console(self, text):
        self.econsole.write(text)

    def on_yankid(self):
        id = os.environ["SELECTED_ID"]
        self.write_to_console(f"Yanked ID: {id}")
        pyperclip.copy(id)

    async def on_elist_view_item_selected(self, event):
        await self.shortcuts_display.update_view(self.get_current_conf().get_shortcuts(),self.get_current_conf().conf_path)


if __name__ == "__main__":
    log("--------------------------------------------------------------------------------")
    conf_path = None
    if len(sys.argv) > 1:
        conf_path = sys.argv[1]

    app = ExecutorApp(conf_path)
    app.run()
