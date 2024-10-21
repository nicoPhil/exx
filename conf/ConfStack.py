from conf.Conf import Conf


class ConfStack:
    def __init__(self):
        self.stack = []

    def push(self, conf: Conf):
        self.stack.append(conf)

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def get_previous(self):
        return self.stack[-2]

    def size(self):
        return len(self.stack)

    def only_one(self):
        return len(self.stack) == 1
