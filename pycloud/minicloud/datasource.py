import json
from pycloud.core.cloud import Policy, Task, Operation, Environment, Host

class JsonDataSource():
    def __init__(self, path):
        self._path = path

        self.hosts = []
        self.envs = []
        self.tasks = []
        self.operations = []
        self.policies = []

    def __str__(self):
        return '[Cloud data source loaded from {}]'.format(self._path)
        
    def _load(self, key):
        with open(self._path, 'rb') as f:
            encrypted_data = f.read()
        json_data = key.decrypt(encrypted_data)
        data = json.loads(json_data)

        self.hosts = [self._load_host(host_dat) for host_data in data.get('hosts', [])]
        self.envs = [self._load_env(env_dat) for env_data in data.get('envs', [])]
        self.operations = [self._load_operation(operation_dat) for operation_data in data.get('operations', [])]
        self.tasks = [self._load_task(task_dat) for task_data in data.get('tasks', [])]
        self.policies = [self._load_policy(policy_dat) for policy_data in data.get('policies', [])]

    def _load_host(self, source):
        return Host(**source)
    def _load_env(self, source):
        return Environment(**source)
    def _load_operation(self, source):
        return Operation(**source)
    def _load_task(self, source):
        return Task(**source)
    def _load_policy(self, source):
        return Policy(**source)

    def _dump_host(self, source):
        return [vars(host) for host in self.hosts]
    def _dump_env(self, source):
        return [vars(env) for env in self.envs]
    def _dump_operation(self, source):
        return [vars(operation) for operation in self.operations]
    def _dump_task(self, source):
        return [vars(task) for task in self.tasks]
    def _dump_policy(self, source):
        return [vars(policy) for policy in self.policies]

    def _save(self, key):
        data = {
            'hosts': [self._dump_host(host) for host in self.hosts],
            'tasks': [self._dump_task(task) for task in self.tasks],
            'operations': [self._dump_operation(operation) for operation in self.operations],
            'envs': [self._dump_env(env) for env in self.envs],
            'policies': [self._dump_policy(policy) for policy in self.policies],
        }
        json_data = json.dumps(data)
        encrypted_data = key.encrypt(json_data)
        with open(self._path, 'wb') as f:
            f.write(encrypted_data)
