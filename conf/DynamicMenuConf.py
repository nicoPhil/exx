from .Conf import Conf
from executor.CommandExecutor import execute_command_and_get_items, execute_string_command
from utils.logger import log
import json

class DynamicMenuConf(Conf):
    def __init__(self, confDict, conf_path, parent_conf=None):
        super().__init__(confDict, conf_path, parent_conf)
        self.validate_conf()

    def validate_conf(self):
        if "type" not in self.confDict:
            return {
                "validated": False,
                "errorMessage": "DynamicMenuConf: type is required"
            }
        if self.confDict["type"] != "dynamicmenu":
            return {
                "validated": False,
                "errorMessage": f"DynamicMenuConf: type must be 'dynamicmenu', got {self.confDict['type']}"
            }
        if "command" not in self.confDict:
            return {
                "validated": False,
                "errorMessage": "DynamicMenuConf: command is required"
            }
        if not isinstance(self.confDict["command"], dict):
            return {
                "validated": False,
                "errorMessage": "DynamicMenuConf: command must be a dict"
            }
        commandDict = self.confDict["command"]
        if "command" not in commandDict:
            return {
                "validated": False,
                "errorMessage": "DynamicMenuConf: command.command is required"
            }
        if not isinstance(commandDict["command"], str):
            return {
                "validated": False,
                "errorMessage": "DynamicMenuConf: command.command must be a string"
            }
        return {
            "validated": True,
            "errorMessage": None
        }

    def _is_str_json(self, str):
        try:
            json.loads(str)
            return True
        except json.JSONDecodeError:
            return False

    def _get_key_and_values_from_json(self, items:str) -> list[str]:
        items_json = json.loads(items)
        result = []
        for key, value in items_json.items():
            if isinstance(value, dict):
                values = value.get('values', str(value))
            else:
                values = str(value)

            result.append({"key": key, "values": values})
        return result

    def _get_key_and_values_from_tab_separated_string(self, items:str) -> list[str]:
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

    def _get_key_and_values(self, items:str) -> list[str]:
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

        if not result["success"]:
            return []

        items = result["items"]
        items_to_return = self._get_key_and_values(items)

        return items_to_return

    def on_select(self):
        if "on_select" in self.confDict:
            execute_string_command(self.confDict["on_select"])
        else:
            log(f"DynamicMenuConf: on_select: no on_select command")
    
    def get_goin_id(self, selected_id):
        if not "goin" in self.confDict:
            raise ValueError("DynamicMenuConf: goin is required")
        return self.confDict["goin"]

    async def on_goin(self):
        if "on_goin" in self.confDict:
            await execute_string_command(self.confDict["on_goin"], self.conf_path)
        else:
            log(f"DynamicMenuConf: on_goin: no on_goin command")

    async def on_goout(self):
        if "on_goout" in self.confDict:
            await execute_string_command(self.confDict["on_goout"], self.conf_path)

   



