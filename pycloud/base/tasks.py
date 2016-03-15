from ..core.cloud import BaseTask

class BashTask(BaseTask):
    command = 'echo "Hello World"'

    required_options = ('command', )

    def shell(self, client):
        result = client.execute(self.options['command'])
        return self.parse_results(*result)

    def parse_results(self, exit_code, out, err):
        if exit_code:
            return err
        else:
            return out
