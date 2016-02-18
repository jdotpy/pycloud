from quickconfig import Configuration
from .security import generate_secret_key, KeyPair

class Cloud():
    def __init__(self, config=None):
        if config is None:
            config = {}
        if not isinstance(config, Configuration):
            config = Configuration(config)
        self.config = config

class Host():
    def __init__(self, hostname, username=None, password=None, pkey=None, name=None):
        if name is None:
            name = hostname

        self.hostname = hostname
        self.username = username
        self.password = password
        self.pkey = pkey
        self.name = name

    def credentials(self):
        return {
            'username': self.username,
            'password': self.password
        }
        

class Operation():
    pass

class Task():
    pass

class HostQuery():
    pass
