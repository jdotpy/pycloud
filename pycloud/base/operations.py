from ..core.cloud import BaseOperation

class SimpleOperation(BaseOperation):
    required_options = ('hosts', 'tasks')

    def run(self):
        for task in self.options['tasks']:
            task.run(self.options['hosts'])

