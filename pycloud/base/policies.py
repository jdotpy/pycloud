from ..core.policies import BasePolicyType

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
