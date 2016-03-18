import json
from pycloud.core.cloud import Environment, Host, Cloud
from pycloud.core.security import EncryptedJsonFile 

class LocalCloud(Cloud):
    def _load_datasource(self):
        with EncryptedJsonFile(self.config.get('datasource'), self.config.get('secret_key'), 'r') as f:
            data = f.read()
        self._hosts = {name: self._load_host(host_data) for name, host_data in data.get('hosts', {}).items()}
        self._envs = {name: self._load_env(env_data) for name, env_data in data.get('envs', {}).items()}
        self._operations = {name: self._load_operation(operation_data) for name, operation_data in data.get('operations', {}).items()}
        self._tasks = {name: self._load_task(task_data) for name, task_data in data.get('tasks', {}).items()}
        self._policies = {name: self._load_policy(policy_data) for name, policy_data in data.get('policies', {}).items()}

    def __str__(self):
        return '[LocalCloud loaded from {}]'.format(self.config.get('datasource')) 

    def _load_host(self, source):
        return Host(cloud=self, **source)
    def _load_env(self, source):
        return Environment(**source)
    def _load_operation(self, source):
        return source
    def _load_task(self, source):
        print('Loading task:', source)
        type_name = source.pop('type', None)
        cls = self._task_types.get(type_name)
        if cls is None:
            return None
        return cls(**source)
    def _load_policy(self, source):
        return source

    def _dump_host(self, source):
        data = {key: getattr(source, key) for key in ('hostname', 'name', 'tags', 'env', 'username', 'password')}
        return data
    def _dump_env(self, source):
        data = {key: getattr(source, key) for key in ()}
        return data
    def _dump_operation(self, source):
        data = {key: getattr(source, key) for key in ()}
        data['type'] = source.get_type_name()
        return data
    def _dump_task(self, source):
        data = {key: getattr(source, key) for key in ('options','name')}
        data['type'] = source.get_type_name()
        return data
    def _dump_policy(self, source):
        data = {key: getattr(source, key) for key in ()}
        data['type'] = source.get_type_name()
        return data

    def _save(self):
        data = {
            'hosts': {name: self._dump_host(host) for name, host in self._hosts.items()},
            'tasks': {name: self._dump_task(task) for name, task in self._tasks.items()},
            'operations': {name: self._dump_operation(operation) for name, operation in self._operations.items()},
            'envs': {name: self._dump_env(env) for name, env in self._envs.items()},
            'policies': {name: self._dump_policy(policy) for name, policy in self._policies.items()},
        }
        with EncryptedJsonFile(self.config.get('datasource'), self.config.get('secret_key'), 'w') as f:
            f.write(data)
