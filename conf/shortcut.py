class Shortcut:
    def __init__(self, key, dict):
        self.key = key
        self.label = dict["label"]
        self.action = dict["action"]
        self.condition = dict.get("condition", None)

    def is_conditional(self):
        return self.condition is not None

    def get_condition_command(self):
        return self.condition["command"]

    def get_action(self):
        return self.action

    def has_action(self):
        return self.action is not None
