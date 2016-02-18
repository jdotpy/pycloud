import paramiko
import threading
import time

class SSHSession(threading.Thread):
    HOST_KEY_POLICY = paramiko.AutoAddPolicy()
    MAX_RECV_BYTES = 1000000
    ENCODING = 'utf-8'

    def __init__(self, host, commands=None, cloud=None, stream=None):
        self.host = host
        self.commands = commands
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(self.HOST_KEY_POLICY)
        self.stream = stream
        self.output = []
        super(SSHSession, self).__init__()

    def run(self):
        self.client.connect(
            self.host.name, 
            **self.host.credentials()
        )
        for cmd in self.commands:
            channel = self.client.get_transport().open_session()
            stdout = b''
            stderr = b''
            channel.exec_command(cmd)
            exit_status = None
            while True:
                if channel.exit_status_ready():
                    exit_status = channel.recv_exit_status()
                if channel.recv_stderr_ready():
                    stderr += channel.recv_stderr(self.MAX_RECV_BYTES)
                if channel.recv_ready():
                    stdout += channel.recv(self.MAX_RECV_BYTES)
                if exit_status is not None:
                    break
                time.sleep(.1)
            self.output.append(
                (exit_status, stdout.decode('utf-8'), stderr.decode('utf-8'))
            )
        self.client.close()

class SSHGroup():
    def __init__(self, hosts, max_pool_size=10):
        self.hosts = hosts
        self.pool_size = min(len(self.hosts), max_pool_size)

    def run_command(self, command):
        return self.run_commands([command])

    def run_commands(self, commands):
        self._exec_pool(commands)

    def _exec_pool(self, commands):
        queue = set(self.hosts)
        threads = set() 
        all_complete = set()

        while len(queue) > 0 or len(threads) > 0:
            print('{} hosts queued, {} active, {} complete'.format(
                len(queue), len(threads), len(all_complete)
            ))
            # Remove any complete/failed threads from our queue 
            complete = []
            for t in list(threads):
                if not t.is_alive():
                    complete.append(t)
                    all_complete.add(t)
            for t in complete:
                print(t.host.name, t.output)
                threads.remove(t)

            # Spin up threads to match pool size
            if len(queue) > 0:
                to_make = self.pool_size - len(threads)
                for i in range(to_make):
                    new_thread = SSHSession(queue.pop(), commands=commands)
                    threads.add(new_thread)
                    new_thread.start()
            time.sleep(.2)
