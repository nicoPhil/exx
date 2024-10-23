from .Conf import Conf, ConfValidationResult
from executor.CommandExecutor import (
    execute_command_and_get_items,
    execute_string_command,
)
from utils.logger import log
import json


class DynamicMenuConf(Conf):
    def __init__(self, confDict, conf_path, parent_conf=None):
        super().__init__(confDict, conf_path, parent_conf)
        self.validate_conf()

    def validate_conf(self) -> ConfValidationResult:
        validation_result = super().validate_conf()
        if not validation_result.validated:
            return validation_result
        if "type" not in self.confDict:
            return ConfValidationResult.get_no_validation_result(
                "DynamicMenuConf: type is required",
            )
        if self.confDict["type"] != "dynamicmenu":
            return ConfValidationResult.get_no_validation_result(
                f"DynamicMenuConf: type must be 'dynamicmenu', got {self.confDict['type']}",
            )
        if "command" not in self.confDict:
            return ConfValidationResult.get_no_validation_result(
                "DynamicMenuConf: command is required",
            )
        if not isinstance(self.confDict["command"], dict):
            return ConfValidationResult.get_no_validation_result(
                "DynamicMenuConf: command must be a dict",
            )
        commandDict = self.confDict["command"]
        if "command" not in commandDict:
            return ConfValidationResult.get_no_validation_result(
                "DynamicMenuConf: command.command is required",
            )
        if not isinstance(commandDict["command"], str):
            return ConfValidationResult.get_no_validation_result(
                "DynamicMenuConf: command.command must be a string",
            )
        return ConfValidationResult.get_validation_result()

    def _is_str_json(self, str):
        try:
            json.loads(str)
            return True
        except json.JSONDecodeError:
            return False

    def _get_key_and_values_from_json(self, items: str) -> list[dict]:
        items_json = json.loads(items)
        result: list[dict] = []
        for key, value in items_json.items():
            if isinstance(value, dict):
                values = value.get("values", str(value))
            else:
                values = str(value)

            result.append({"key": key, "values": values})
        return result

    def _get_key_and_values_from_tab_separated_string(self, items: str) -> list[dict]:
        lines = items.splitlines()

        result = []
        for line in lines:
            fields = line.split("\t")
            key = None
            values = None
            if len(fields) >= 2:
                key = fields[0]
                values = "\t".join(fields[1:])
            else:
                key = fields[0]
                values = fields[0]

            result.append({"key": key, "values": values})

        return result

    def _get_key_and_values(self, items: str) -> list[dict]:
        add_key_to_values = self.conf_validator.getBooleanOrFalse("add_key_to_values")
        result = []
        if self._is_str_json(items):
            result = self._get_key_and_values_from_json(items)
        else:
            result = self._get_key_and_values_from_tab_separated_string(items)

        if add_key_to_values:
            for item in result:
                item["values"] = f"{item['key']}\t{item['values']}"

        return result

    async def get_items(self):
        command = self.confDict["command"]
        result = await execute_command_and_get_items(command, self.conf_path)

        if not result.success:
            return []

        items = result.output
        items_to_return = self._get_key_and_values(items)

        return items_to_return

    async def on_select(self):
        if "on_select" in self.confDict:
            await execute_string_command(self.confDict["on_select"], self.conf_path)
        else:
            log("DynamicMenuConf: on_select: no on_select command")

    def get_goin_id(self, selected_id):
        if "goin" not in self.confDict:
            raise ValueError("DynamicMenuConf: goin is required")
        return self.confDict["goin"]

    async def on_goin(self):
        if "on_goin" in self.confDict:
            await execute_string_command(self.confDict["on_goin"], self.conf_path)
        else:
            log("DynamicMenuConf: on_goin: no on_goin command")

    async def on_goout(self):
        if "on_goout" in self.confDict:
            await execute_string_command(self.confDict["on_goout"], self.conf_path)
