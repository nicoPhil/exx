from utils.logger import log


class ConfValidator:
    def __init__(self, conf):
        self.conf = conf

    def get_trueish_values(self):
        return ["true", "t", "yes", "y", "1", True]

    def get_falseish_values(self):
        return ["false", "f", "no", "n", "0", False]

    def _can_be_bool(self, str):
        if isinstance(str, bool):
            return True
        if (
            str.lower() in self.get_trueish_values()
            or str.lower() in self.get_falseish_values()
        ):
            return True
        else:
            return False

    def get_value_as_bool(self, str):
        if not self._can_be_bool(str):
            raise ValueError(
                f"ConfValidator: get_value_as_bool: {str} is not a boolean"
            )

        if str in self.get_trueish_values():
            return True
        else:
            return False

    def has_key(self, key):
        return key in self.conf

    def getBooleanOrTrue(self, key):
        if not self.has_key(key):
            return True
        return self.get_value_as_bool(self.conf[key])

    def getBooleanOrFalse(self, key):
        log(self.conf)
        if not self.has_key(key):
            return False
        return self.get_value_as_bool(self.conf[key])
