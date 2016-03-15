from .utils import import_obj

class BaseModule():
    name = ''

    policy_types = []
    task_types = []
    operation_types = []

    def _import_from_string(self, path):
        return import_obj(path)

    def get_task_types(self):
        tasks = {}
        for path in self.task_types:
            cls = self._import_from_string(path)
            tasks[cls.__name__] = cls
        return tasks

    def get_operation_types(self):
        operations = {}
        for path in self.operation_types:
            cls = self._import_from_string(path)
            operations[cls.__name__] = cls
        return operations

    def get_policy_types(self):
        policies = {}
        for path in self.policy_types:
            cls = self._import_from_string(path)
            policies[cls.__name__] = cls
        return policies
