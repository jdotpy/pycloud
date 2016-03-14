from .net import BaseShellHandler

class BasePolicyType():
    pass


class DirPolicy():
    def __init__(self, path=None):
        self.path = path


class PolicyShellHandler(BaseShellHandler):
    pass
