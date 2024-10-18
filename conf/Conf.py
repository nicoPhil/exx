from utils.logger import log
from executor.CommandExecutor import execute_string_command
from conf.ConfValidator import ConfValidator
import os
class Conf():
    def __init__(self, confDict, conf_path, parent_conf=None):
        self.confDict = confDict
        validation_result = self.validate_conf()
        if not validation_result["validated"]:
            raise ValueError(f"Conf: {validation_result['errorMessage']}")

        self.inherit_shortcuts = True
        self.parent_conf = parent_conf
        self.conf_path = conf_path
        self.conf_validator = ConfValidator(self.confDict)
        self.conf_timestamp = os.path.getmtime(self.conf_path)


    def is_conf_file_modified(self):
        mtime = os.path.getmtime(self.conf_path)    
        if mtime != self.conf_timestamp:
            return True
        return False

    def is_conf_obsolete(self):
        return self.is_conf_file_modified() 

    async def async_init(self):
        await self.init_if_needed()

    def validate_conf(self):
        confDict = self.confDict
        if "type" not in confDict:
            return {
                "validated": False,
                "errorMessage": "Conf: type is required"
            }
        if "inherit_shortcuts" in confDict:
            if not isinstance(confDict["inherit_shortcuts"], bool):
                return {
                    "validated": False,
                    "errorMessage": "Conf: inherit_shortcuts must be a boolean"
                }
            self.inherit_shortcuts = confDict["inherit_shortcuts"]

        if "on_init" in confDict:
            if not isinstance(confDict["on_init"], str):
                return {
                    "validated": False,
                    "errorMessage": "Conf: on_init must be a string"
                }
        if "shortcuts" in confDict:
            if not isinstance(confDict["shortcuts"], list):
                return {
                    "validated": False,
                    "errorMessage": "Conf: shortcuts must be a list"
                }
            for shortcut in confDict["shortcuts"]:
                if not isinstance(shortcut, dict):
                    return {
                        "validated": False,
                        "errorMessage": "Conf: shortcut must be a dictionary"
                        }
                if "key" not in shortcut:
                    return {
                        "validated": False,
                        "errorMessage": "Conf: key is required in shortcut"
                    }
                if "label" not in shortcut:
                    return {
                        "validated": False,
                        "errorMessage": "Conf: label is required in shortcut"
                    }
                if "action" not in shortcut:
                    return {
                        "validated": False,
                        "errorMessage": "Conf: action is required in shortcut"
                    }
        return {
            "validated": True,
            "errorMessage": None
        }

    def has_init(self):
        return "on_init" in self.confDict

    def get_init_command(self):
        if not self.has_init():
            return None
        return self.confDict["on_init"]

    async def init_if_needed(self):
        if self.has_init():
            await execute_string_command(self.get_init_command(),self.conf_path)

    def has_shortcuts(self):
        if self.get_shortcuts() is None:
            return False
        return True

    def has_parent_conf(self):
        return self.parent_conf is not None

    def get_shortcuts(self):
        if not self.has_parent_conf() or not self.does_inherit_shortcuts():
            return self.confDict.get("shortcuts", [])
        shortcuts = []
        if self.has_parent_conf() and self.does_inherit_shortcuts():
            shortcuts.extend(self.parent_conf.get_shortcuts() or [])
        
        local_shortcuts = self.confDict.get("shortcuts", [])
        
        shortcut_dict = {s["key"]: s for s in shortcuts}
        
        for local_shortcut in local_shortcuts:
            shortcut_dict[local_shortcut["key"]] = local_shortcut
        
        ret = list(shortcut_dict.values())
        return ret

    def get_shortcut(self, key):
        shortcuts = self.get_shortcuts()
        for shortcut in shortcuts:
            if shortcut["key"] == key:
                return shortcut
        return None

    def is_shortcut(self, key):
        ret= self.get_shortcut(key) is not None
        return ret

    def does_inherit_shortcuts(self):
        return self.inherit_shortcuts

    async def on_goin(self):
        pass

    async def on_goout(self):
        pass

