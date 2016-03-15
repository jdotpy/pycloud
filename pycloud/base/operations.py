
class SimpleOperation():
    def __init__(self, tasks, hosts):
        self.hosts = hosts
        self.tasks = tasks

    def run(self):
        for task in tasks:
            task.run(hosts)

