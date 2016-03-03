from quickconfig import Configuration
from .security import generate_secret_key, KeyPair
from .net import SSHGroup
import re

class Cloud():
    DEFAULT_KEY_NAME = 'default'

    def __init__(self, config=None, **kwargs):
        # Configuration
        if config is None:
            config = {}
        if not isinstance(config, Configuration):
            config = Configuration(config)
        self.config = config

        self._load_keys(config.get('keys', {}))
        self._load_datasource(**kwargs)

    def _load_keys(self, key_source):
        keys = {}
        for key_name, key_data in key_source.items():
            key = KeyPair(**key_data)
            keys[key_name] = key
        self.keys = keys
        self.key = keys.get('default', None)

    def _load_datasource(self, **data):
        # Datasource
        self._hosts = data.pop('hosts', [])
        self._envs = data.pop('envs', [])
        self._operations = data.pop('operations', [])
        self._tasks = data.pop('tasks', [])
        self._policies = data.pop('policies', [])

    def query(self, filters, single=False):
        matches = []
        name_pattern = filters.get('name', None)
        if name_pattern:
            name_pattern = re.compile(name_pattern)
        tags = filters.get('tags', None)
        env = filters.get('env', None)
        for host in self.hosts:
            if name_pattern and not name_pattern.match(host.name):
                continue
            if tags and tags not in host.tags:
                continue
            if env and host.env != env:
                continue
            if single:
                return host
            else:
                matches.append(host)
        return matches

    @property
    def hosts(self):
        return self._hosts

    @property
    def tasks(self):
        return self._tasks

    @property
    def envs(self):
        return self._envs

    @property
    def policies(self):
        return self._policies

    @property
    def operations(self):
        return self._operations

class Host():
    def __init__(self, hostname, username=None, password=None, pkey=None, name=None, env=None, tags=None, cloud=None):
        if name is None:
            name = hostname

        self.hostname = hostname
        self.username = username
        self.password = password
        self.pkey = pkey
        self.name = name
        self.env = env
        self.tags = tags
        self.cloud = cloud

    def credentials(self):
        username = self.username
        if not self.username:
            print('Falling back to root user')
            username = 'root'
        creds = {
            'username': username
        }
        if self.password:
            creds['password'] = self.password
        elif self.pkey:
            creds['pkey'] = self.pkey.as_paramiko()
        elif self.cloud:
            creds['pkey'] = self.cloud.key.as_paramiko()
        return creds

    def ping(self):
        results = SSHGroup([self]).run_commands([])
        return results.results[self]

    def __str__(self):
        return '[{}] {}'.format(self.env, self.name)

        
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
