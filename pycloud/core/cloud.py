from quickconfig import Configuration
from .security import generate_secret_key, KeyPair
from .datasource import BasicDataSource

class Cloud():
    def __init__(self, config=None, datasource=None):
        # Configuration
        if config is None:
            config = {}
        if not isinstance(config, Configuration):
            config = Configuration(config)
        self.config = config

        # Datasource
        if datasource is None:
            datasource = BasicDataSource()
        self.datasource = datasource

        # Key
        private_key_str = config.get('private_key', None)
        if private_key_str:
            self.key = KeyPair(private_key_str)
        else:
            self.key = None

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

class Policy():
    pass

class Environment():
    pass
