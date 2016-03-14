from .net import BaseShellHandler

class PolicyShellHandler(BaseShellHandler):
    def __init__(self, policy):
        self.policy = policy

    def shell(self, client):
        self.policy.enforce(client)

class BasePolicyType():
    required_options = []

    def shell_handler(self):
        return PolicyShellHandler

    def __init__(self, options=None):
        self.options = options or {}
        for option_name in self.required_options:
            if option_name not in self.options:
                raise ValueError('Policy requires option: ' + option_name)

    def enforce(self, client):
        raise NotImplemented()

class BasePolicySet(BasePolicyType):
    def __init__(self, sub_policies):
        self.sub_policies = sub_policies

    def enforce(self, client):
        for child in self.sub_policies:
            child.enforce()

class Dir(BasePolicyType):
    required_options = ('path',)

    def status(self):
        path = self.options['path']
        exit_status, out, err = self.client.execute('stat {}'.format(path))
        exists = not exit_status
        return {'exists': exists}

    def create(self):
        path = self.options['path']
        exit_status, out, err = self.client.execute('mkdir {}'.format(path))
        if exit_status:
            return False
        return True

    def enforce(self, client):
        self.client = client
        status = self.status()
        if status['exists']:
            print('Dir exists')
        else:
            print('Dir will be created')
            self.create()
