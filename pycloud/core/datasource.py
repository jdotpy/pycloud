
class BasicDataSource():
    def __init__(self, *args, **kwargs):
        self.hosts = kwargs.pop('hosts', [])
        self.envs = kwargs.pop('envs', [])
        self.operations = kwargs.pop('operations', [])
        self.tasks = kwargs.pop('tasks', [])
        self.policies = kwargs.pop('policies', [])

    def query(self, datatype, filters, single=False):
        matches = []
        for item in getattr(self, datatype):
            for attr, value in filters.items():
                if getattr(item, attr, None) != value:
                    continue
                if single:
                    return item
                else:
                    matches.append(item)
        return matches
