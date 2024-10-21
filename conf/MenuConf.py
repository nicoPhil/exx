from .Conf import Conf


class MenuConf(Conf):
    def __init__(self, confDict, conf_path, parent_conf):
        super().__init__(confDict, conf_path, parent_conf)

    def validate_conf(self):
        validation_result = super().validate_conf()
        if not validation_result["validated"]:
            return validation_result
        if "type" not in self.confDict:
            return {"validated": False, "errorMessage": "MenuConf: type is required"}
        if self.confDict["type"] != "menu":
            return {
                "validated": False,
                "errorMessage": f"MenuConf: type must be 'menu', got {self.confDict['type']}",
            }
        if "items" not in self.confDict:
            return {"validated": False, "errorMessage": "MenuConf: items is required"}
        if not isinstance(self.confDict["items"], list):
            return {
                "validated": False,
                "errorMessage": "MenuConf: items must be a list",
            }
        for item in self.confDict["items"]:
            if "id" not in item:
                return {
                    "validated": False,
                    "errorMessage": "MenuConf: item id is required",
                }
            if "label" not in item:
                return {
                    "validated": False,
                    "errorMessage": "MenuConf: item label is required",
                }
            if "goin" not in item:
                return {
                    "validated": False,
                    "errorMessage": "MenuConf: item goin is required",
                }
        return {"validated": True, "errorMessage": None}

    async def get_items(self):
        return self.confDict["items"]

    def get_goin_id(self, selected_id):
        for item in self.confDict["items"]:
            if item["id"] == selected_id:
                return item["goin"]
        return None
