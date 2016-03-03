import json
from pycloud.core.cloud import Policy, Task, Operation, Environment, Host, Cloud
from pycloud.core.security import EncryptedJsonFile 

class LocalCloud(Cloud):
    def __init__(self, path, **kwargs):
        self._path = path
        super(LocalCloud, self).__init__(**kwargs)

    def _load_datasource(self):
        with EncryptedJsonFile(self._path, self.key, 'r') as f:
            data = f.read()
        self._hosts = [self._load_host(host_data) for host_data in data.get('hosts', [])]
        self._envs = [self._load_env(env_data) for env_data in data.get('envs', [])]
        self._operations = [self._load_operation(operation_data) for operation_data in data.get('operations', [])]
        self._tasks = [self._load_task(task_data) for task_data in data.get('tasks', [])]
        self._policies = [self._load_policy(policy_data) for policy_data in data.get('policies', [])]

    def __str__(self):
        return '[LocalCloud loaded from {}]'.format(self._path) 

    def _load_host(self, source):
        return Host(cloud=self, **source)
    def _load_env(self, source):
        return Environment(**source)
    def _load_operation(self, source):
        return Operation(**source)
    def _load_task(self, source):
        return Task(**source)
    def _load_policy(self, source):
        return Policy(**source)

    def _dump_host(self, source):
        return {key: getattr(source, key) for key in ('hostname', 'name', 'tags', 'env', 'username', 'password')}
    def _dump_env(self, source):
        return {key: getattr(source, key) for key in ()}
    def _dump_operation(self, source):
        return {key: getattr(source, key) for key in ()}
    def _dump_task(self, source):
        return {key: getattr(source, key) for key in ()}
    def _dump_policy(self, source):
        return {key: getattr(source, key) for key in ()}

    def _save(self):
        data = {
            'hosts': [self._dump_host(host) for host in self.hosts],
            'tasks': [self._dump_task(task) for task in self.tasks],
            'operations': [self._dump_operation(operation) for operation in self.operations],
            'envs': [self._dump_env(env) for env in self.envs],
            'policies': [self._dump_policy(policy) for policy in self.policies],
        }
        with EncryptedJsonFile(self._path, self.key, 'w') as f:
            f.write(data)

    def add(self, obj):
        if isinstance(obj, Host):
            self.hosts.append(host)

