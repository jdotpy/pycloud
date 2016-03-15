from quickconfig import Configuration
from .security import generate_secret_key, KeyPair, AESEncryption
from .net import SSHGroup
from . import policies
from .utils import import_obj
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
        self._load_modules(config.get('modules', []))

    def _load_keys(self, key_source):
        keys = {}
        for key_name, key_data in key_source.items():
            key = KeyPair(password=self.config.get('secret_key'), **key_data)
            keys[key_name] = key
        self.keys = keys
        self.key = keys.get('default', None)

    def _load_datasource(self, **data):
        # Datasource
        self._hosts = data.pop('hosts', {})
        self._envs = data.pop('envs', {})
        self._operations = data.pop('operations', {})
        self._tasks = data.pop('tasks', {})
        self._policies = data.pop('policies', {})

    def _load_modules(self, paths):
        self._policy_types = {}
        self._task_types = {}
        self._operation_types = {}

        self.modules = []
        for path in paths:
            try:
                Module = import_obj(path)
            except ImportError as e:
                print('Error loading module:', e)
                continue
            module = Module()
            self.modules.append(module)

            # Module Triggers
            self._policy_types.update(module.get_policy_types())
            self._operation_types.update(module.get_operation_types())
            self._task_types.update(module.get_task_types())

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
        return self._hosts.values()

    def get_host(self, name):
        return self._hosts.get(name)

    @property
    def tasks(self):
        return self._tasks.values()

    def get_task(self, name):
        return self._tasks.get(name)

    @property
    def envs(self):
        return self._envs.values()

    def get_env(self, name):
        return self._envs.get(name)

    @property
    def policies(self):
        return self._policies.values()

    def get_policy(self, name):
        return self._policies.get(name)

    @property
    def operations(self):
        return self._operations

    def get_operation(self, name):
        return self._operations.get(name)

    def encrypt(self, message):
        return AESEncrypt(self.config('secret_key')).encrypt(message, encode=True)

    def decrypt(self, ciphertext):
        return AESEncrypt(self.config('secret_key')).decrypt(ciphertext)

    def enforce_policy(self, policy, hosts):
        group = SSHGroup(hosts)
        results = group.run_handler(policy.shell_handler(), policy)
        return results

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
        
class BaseOperation():
    hosts = []
    tasks = []

    def get_hosts(self):
        return self.hosts    

    def get_tasks(self):
        return self.tasks

    def run(self):
        for task in self.get_tasks():
            task.run(self.get_hosts(task))

class TaskShellHandler():
    def __init__(self, task):
        self.task = task

    def shell(self, client):
        self.task.shell(client)

class BaseTask():
    required_options = []

    def __init__(self, **options):
        self.options = options

        for option in self.required_options:
            if option not in self.options:
                raise ValueError(str(self) + ' requires option: ' + option)


    def run(self, hosts):
        group = SSHGroup(hosts)
        return group.run_handler(TaskShellHandler, self)

class HostQuery():
    pass

class Environment():
    pass
