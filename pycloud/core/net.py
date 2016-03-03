import paramiko
import threading
import time

class SSHError():
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class NetworkError(SSHError):
    pass

class AuthError(SSHError):
    pass

class SSHResult():
    def __init__(self, executed=True, output=None, error=None):
        self.executed = executed
        self.output = output or []
        self.error = error

    def __str__(self):
        if not self.executed:
            if self.error:
                return 'Error:' + str(self.error)
            else:
                return 'Unknown Communication Error'
        if self.success():
            return 'Success'
        else:
            return 'Failed'

    def success(self):
        if self.error:
            return False
        for exit_code, stdout, stderr in self.output:
            if exit_code != 0:
                return False
        return True

class SSHGroupResult():
    def __init__(self):
        self.results = {}

    def _add_result(self, host, result):
        self.results[host] = result

    def __str__(self):
        return self.display()

    def display(self, show_stderr=False, show_stdout=False, show_summary=True):
        output = []
        for host, result in self.results.items():
            for exit_code, stdout, stderr in result.output:
                if show_stdout and stdout:
                    for line in stdout.splitlines():
                        output.append('{}<<out>>: {}'.format(host, line))
                if show_stderr and stderr:
                    for line in stderr.splitlines():
                        output.append('{}<<err>>: {}'.format(host, line))
            if not result.executed or show_summary:
                output.append('{}: {}'.format(host, result))
        return '\n'.join(output)

    def success(self):
        for result in self.results.values():
            if not result.no_errors():
                return False
        return True

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
        self.cloud = cloud
        super(SSHSession, self).__init__()

    def run(self):
        try:
            self.client.connect(
                self.host.name, 
                **self.host.credentials()
            )
        except (OSError, paramiko.ssh_exception.SSHException) as e:
            self.result = SSHResult(executed=False, error=SSHError(str(e)))
            return False
        except paramiko.ssh_exception.AuthenticationException as e:
            self.result = SSHResult(executed=False, error=AuthError())
            return False
        except Exception as e:
            self.result = SSHResult(executed=False, error=e)
            return False
            
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
        self.result = SSHResult(executed=True, output=self.output)
        self.client.close()
        return True, self.output

class SSHGroup():
    def __init__(self, hosts, max_pool_size=10):
        self.hosts = hosts
        self.pool_size = min(len(self.hosts), max_pool_size)

    def run_command(self, command):
        return self.run_commands([command])

    def run_commands(self, commands):
        return self._exec_pool(commands)

    def _exec_pool(self, commands):
        queue = set(self.hosts)
        threads = set() 
        all_complete = set()

        results = SSHGroupResult()
        while len(queue) > 0 or len(threads) > 0:
            # Remove any complete/failed threads from our queue 
            complete = []
            for t in list(threads):
                if not t.is_alive():
                    complete.append(t)
                    all_complete.add(t)
            for t in complete:
                results._add_result(t.host, t.result)
                threads.remove(t)

            # Spin up threads to match pool size
            if len(queue) > 0:
                to_make = self.pool_size - len(threads)
                for i in range(to_make):
                    new_thread = SSHSession(queue.pop(), commands=commands)
                    threads.add(new_thread)
                    new_thread.start()
            time.sleep(.2)
        return results
