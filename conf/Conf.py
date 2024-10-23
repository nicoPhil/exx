from executor.CommandExecutor import execute_string_command
from conf.ConfValidator import ConfValidator
from conf.shortcut import Shortcut
import os
from utils.logger import log


class ConfValidationResult:
    def __init__(self, validated: bool, errorMessage: str | None):
        self.validated = validated
        self.errorMessage = errorMessage

    @staticmethod
    def get_no_validation_result(
        errorMessage: str | None = None,
    ) -> "ConfValidationResult":
        return ConfValidationResult(False, errorMessage)

    @staticmethod
    def get_validation_result() -> "ConfValidationResult":
        return ConfValidationResult(True, None)


class Conf:
    def __init__(self, confDict, conf_path, parent_conf=None):
        self.confDict = confDict
        validation_result = self.validate_conf()
        if not validation_result.validated:
            raise ValueError(f"Conf: {validation_result.errorMessage}")

        self.inherit_shortcuts = True
        self.parent_conf = parent_conf
        self.conf_path = conf_path
        self.conf_validator = ConfValidator(self.confDict)
        self.conf_timestamp = os.path.getmtime(self.conf_path)

        log(f"Conf: {self.confDict}")

    def is_conf_file_modified(self):
        mtime = os.path.getmtime(self.conf_path)
        if mtime != self.conf_timestamp:
            return True
        return False

    def is_conf_obsolete(self):
        return self.is_conf_file_modified()

    async def async_init(self):
        await self.init_if_needed()

    def is_shortcuts_list(self) -> bool:
        return isinstance(self.confDict["shortcuts"], list)

    def is_shortcuts_dict(self) -> bool:
        return isinstance(self.confDict["shortcuts"], dict)

    def validate_conf_shortcuts_as_list(self) -> ConfValidationResult:
        confDict = self.confDict
        if "shortcuts" in confDict:
            if not isinstance(confDict["shortcuts"], list):
                return ConfValidationResult.get_no_validation_result(
                    "Conf: shortcuts must be a list",
                )
            for shortcut in confDict["shortcuts"]:
                if not isinstance(shortcut, dict):
                    return ConfValidationResult.get_no_validation_result(
                        "Conf: shortcut must be a dictionary",
                    )
                if "key" not in shortcut:
                    return ConfValidationResult.get_no_validation_result(
                        "Conf: key is required in shortcut",
                    )
                if "label" not in shortcut:
                    return ConfValidationResult.get_no_validation_result(
                        "Conf: label is required in shortcut",
                    )
                if "action" not in shortcut:
                    return ConfValidationResult.get_no_validation_result(
                        "Conf: action is required in shortcut",
                    )
        return ConfValidationResult.get_validation_result()

    def validate_conf_shortcuts_as_dict(self) -> ConfValidationResult:
        confDict = self.confDict
        if not self.is_shortcuts_dict():
            return ConfValidationResult.get_no_validation_result(
                "Conf: shortcuts must be a dictionary",
            )

        for key, value in confDict["shortcuts"].items():
            if not isinstance(value, dict):
                return ConfValidationResult.get_no_validation_result(
                    f"Conf: shortcut {key} must be a dictionary",
                )

        return ConfValidationResult.get_validation_result()

    def validate_conf_shortcuts(self) -> ConfValidationResult:
        if "shortcuts" not in self.confDict:
            return ConfValidationResult.get_validation_result()

        if self.is_shortcuts_list():
            return self.validate_conf_shortcuts_as_list()
        elif self.is_shortcuts_dict():
            return self.validate_conf_shortcuts_as_dict()
        else:
            return ConfValidationResult.get_no_validation_result(
                "Conf: shortcuts must be a list or a dictionary",
            )

    def validate_conf(self) -> ConfValidationResult:
        confDict = self.confDict
        if "type" not in confDict:
            return ConfValidationResult.get_no_validation_result(
                "Conf: type is required"
            )
        if "inherit_shortcuts" in confDict:
            if not isinstance(confDict["inherit_shortcuts"], bool):
                return ConfValidationResult.get_no_validation_result(
                    "Conf: inherit_shortcuts must be a boolean",
                )
            self.inherit_shortcuts = confDict["inherit_shortcuts"]

        if "on_init" in confDict:
            if not isinstance(confDict["on_init"], str):
                return ConfValidationResult.get_no_validation_result(
                    "Conf: on_init must be a string"
                )

        shortcuts_validation_result = self.validate_conf_shortcuts()
        if not shortcuts_validation_result.validated:
            return shortcuts_validation_result

        return ConfValidationResult.get_validation_result()

    def has_init(self) -> bool:
        return "on_init" in self.confDict

    def get_init_command(self) -> str | None:
        if not self.has_init():
            return None
        return self.confDict["on_init"]

    async def init_if_needed(self) -> None:
        if self.has_init():
            init_command: str | None = self.get_init_command()
            if init_command is not None:
                await execute_string_command(init_command, self.conf_path)

    def has_shortcuts(self) -> bool:
        if self.get_shortcuts() is None:
            return False
        return True

    def has_parent_conf(self) -> bool:
        return self.parent_conf is not None

    def _can_inherit_shortcuts(self) -> bool:
        has_parent_conf: bool = self.has_parent_conf()
        does_inherit_shortcuts: bool = self.does_inherit_shortcuts()
        return has_parent_conf and does_inherit_shortcuts

    def _get_shortcuts_from_conf_list_with_parent(self) -> list[Shortcut]:
        ret: list[Shortcut] = []

        for shortcut_dict in self.confDict.get("shortcuts", []):
            key: str = shortcut_dict["key"]
            ret.append(Shortcut(key, shortcut_dict))

        return ret

    def _get_shortcuts_from_conf_dict_with_parent(self) -> list[Shortcut]:
        ret: list[Shortcut] = []
        for key, shortcut_dict in self.confDict["shortcuts"].items():
            ret.append(Shortcut(key, shortcut_dict))
        return ret

    def _has_local_shortcuts(self) -> bool:
        return "shortcuts" in self.confDict

    def get_shortcuts(self) -> list[Shortcut]:
        ret: list[Shortcut] = []
        if not self._has_local_shortcuts():
            ret = []
        elif self.is_shortcuts_list():
            ret = self._get_shortcuts_from_conf_list_with_parent()
        elif self.is_shortcuts_dict():
            ret = self._get_shortcuts_from_conf_dict_with_parent()
        else:
            raise ValueError("Conf: shortcuts must be a list or a dictionary")

        if self._can_inherit_shortcuts():
            ret.extend(self.parent_conf.get_shortcuts() or [])

        return ret

    def get_shortcut(self, key) -> Shortcut | None:
        shortcuts = self.get_shortcuts()
        for shortcut in shortcuts:
            if shortcut.key == key:
                return shortcut
        return None

    def is_shortcut(self, key) -> bool:
        ret = self.get_shortcut(key) is not None
        return ret

    def does_inherit_shortcuts(self) -> bool:
        return self.inherit_shortcuts

    async def on_goin(self):
        pass

    async def on_goout(self):
        pass

    async def get_items(self):
        pass
