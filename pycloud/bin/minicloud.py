#!/usr/bin/env python

from quickconfig import Configuration
from pycloud.minicloud.utils import new_cloud, path_exists
from pycloud.minicloud.cloud import LocalCloud
from pycloud.core.cloud import Host
from pycloud.core.utils import dumb_argparse
from pycloud.core.net import SSHGroup
from pycloud.core.security import *
from pycloud.core import policies
import argparse
import getpass
import shlex
import sys

class CLIHandler():
    DEFAULT_CONFIG_SOURCES = [
        '/etc/pycloud.yaml',
        '~/.pycloud.yaml',
        'config.yaml'
    ]
    COMMANDS = {
        # command name, function
        'encrypt': {
            'func': 'encrypt',
            'cloud': False,
            'args': [
                'message'
            ]
        },
        'info': {
            'func': 'info',
        },
        'init': {
            'func': 'init',
            'cloud': False,
            'args': [
                ('path', {'help': 'Path to new cloud dir'}),
                (('-k', '--key'), {'help': 'Path to key to use as default'}),
                (('-n', '--name'), {'help': 'Name of cloud'})
            ]
        },
        'shell': {
            'func': 'shell',
            'args': [
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
                (('--summary'), {'action': 'store_true', 'default': False})
            ]
        },
        'enforce': {
            'func': 'enforce',
            'args': [
                ('policy', {'help': 'Policy name'}),
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
                ('--summary', {'action': 'store_true', 'default': False})
            ]
        },
        'create_task': {
            'func': 'create_task',
            'extra': True,
            'args': [
                ('task_type', {'help': 'Task type'}),
                ('task_name', {'help': 'Task name'}),
            ]
        },
        'task': {
            'func': 'task',
            'args': [
                ('task', {'help': 'Task name'}),
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
            ]
        },
        'operation': {
            'func': 'operation',
            'args': [
                ('operation', {'help': 'Operation name'}),
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
            ]
        },
        'ssh': {
            'func': 'ssh',
            'args': [
                ('ssh_command', {'help': 'Command to run'}),
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
                (('--summary'), {'action': 'store_true', 'default': False})
            ]
        },
        'register': {
            'func': 'register',
            'args': [
                ('hostname', {}),
                (('-n','--name'), {}),
                (('-e','--env'), {}),
                (('-t','--tags'), {'nargs': '*'}),
                (('-u','--user'), {}),
                (('-p','--password'), {}),
                (('-P','--ask-for-pass'), {'dest': 'ask_for_pass', 'action': 'store_true', 'default': False}),
            ]
        },
        'hosts': {
            'func': 'hosts',
        }
    }

    def __init__(self):
        self.cloud = None

    def run_command_str(self, text):
        args = parser.parse_args(shlex.split(text))
        self.run_command(args)

    def run_command(self, args):
        options = self._parse_args(args)
        command_name = options.pop('command')
        if not command_name:
            options = self._parse_args(args + ['-h'])

        command = self.COMMANDS[command_name]
        if self.cloud is None and command.get('cloud', True):
            self.cloud = self._setup_cloud(options.pop('config'))
            if self.cloud is None:
                raise ValueError('Could not run command without cloud. Aborting.')
    
        func = getattr(self, command['func'])
        func(**options)

    def _setup_cloud(self, config_file=None):
        if config_file:
            sources = [config_file]
        else:
            sources = self.DEFAULT_CONFIG_SOURCES
        config = Configuration(*sources)
        if config.loaded == 0:
            print('No config files found. Looked in these locations:', sources)
            return None
        try:
            cloud = LocalCloud(config=config)
        except ValueError as e:
            cloud = None
            raise ValueError('Could not configure cloud: ' +  str(e))
        return cloud

    def _parse_args(self, args):
        root_parser = argparse.ArgumentParser(description='Mini cloud!')
        subparsers = root_parser.add_subparsers(dest='command')
        only_known = False
        for cmd_name, cmd_info in self.COMMANDS.items():
            cmd_parser = subparsers.add_parser(cmd_name)
            if cmd_info.get('cloud', True):
                cmd_parser.add_argument('--config', default=None)
            if cmd_info.get('extras', False):
                only_known = False
            for arg_info in cmd_info.get('args', []):
                if isinstance(arg_info, str):
                    cmd_args = [arg_info]
                    cmd_options = {}
                else:
                    cmd_args, cmd_options = arg_info
                if isinstance(cmd_args, str):
                    cmd_args = [cmd_args]
                cmd_parser.add_argument(*cmd_args, **cmd_options)

        extra = None 
        if only_known:
            options = root_parser.parse_args(args)
        else:
            options, extra = root_parser.parse_known_args(args)
            extra = dumb_argparse(extra)
        result = vars(options)
        if extra:
            result['options'] = extra
        return result

    def init(self, path=None, name=None, key=None):
        print('Creating new cloud at:', path)
        if path_exists(path):
            print('Path already exists')
            return False
        new_cloud(path, name=name, key_path=key)

    def info(self):
        print('Pycloud initialized: ', self.cloud)
        print(self.cloud)
        print('{} hosts found'.format(len(self.cloud.hosts)))

    def hosts(self):
        for host in self.cloud.hosts:
            print(host)

    def ssh(self, ssh_command=None, name=None, tags=None, env=None, summary=False):
        hosts = self.cloud.query({'name': name, 'tags': tags, 'env': env})
        if not hosts:
            print('No hosts found!')
            return False
        else:
            print('Found these hosts:')
            for host in hosts:
                print('\t', host)

        group = SSHGroup(hosts, max_pool_size=10)
        ssh_commands = ssh_command.split(';')
        results = group.run_commands(ssh_commands)

        show_stdout = True
        show_stderr = not summary
        print(results.display(show_stderr=show_stderr, show_stdout=show_stdout))

    def shell(self, name=None, tags=None, env=None, summary=False):
        hosts = self.cloud.query({'name': name, 'tags': tags, 'env': env})
        if not hosts:
            print('No hosts found!')
            return False
        else:
            print('Found these hosts:')
            for host in hosts:
                print('\t', host)

        group = SSHGroup(hosts, max_pool_size=10)
        show_stdout = True
        show_stderr = True
        while True:
            try:
                cmd = input("[cloud]$ ")
            except KeyboardInterrupt:
                break
            if not cmd:
                continue
            if cmd == 'exit':
                break
            results = group.run_command(cmd)
            print(results.display(show_summary=False, show_stdout=show_stdout, show_stderr=show_stderr))

    def enforce(self, policy=None, name=None, tags=None, env=None, summary=False):
        hosts = self.cloud.query({'name': name, 'tags': tags, 'env': env})
        if not hosts:
            print('No hosts found!')
            return False
        else:
            print('Found these hosts:')
            for host in hosts:
                print('\t', host)

        policy = policies.Dir(options={'path': '/tmp/my-policy-dir'})
        results = self.cloud.enforce_policy(policy, hosts)
        print(results.display(show_stderr=True))

    def register(self, hostname=None, name=None, tags=None, env='default', user=None, password=None, ask_for_pass=False):
        """ Register a new host """
        if ask_for_pass:
            password = getpass.getpass('Enter password: ')
        if name is None:
            name = hostname
        print('Registering host [{}] {} ({}) (Tags: {}) :: {}'.format(
            env, name, hostname, tags, self.cloud
        ))
        host = Host(hostname, name=name, username=user, password=password, env=env, cloud=self.cloud)
        results = host.ping()
        if results.success():
            print('Connection test successful. Saving host.')
            add = True
        else:
            add_anyway = input('Connection test failed. Save host anyway? (y/n): ')
            if add_anyway != 'y':
                return False
        self.cloud._hosts[host.name] = host
        self.cloud._save()

    def encrypt(self, message=None):
        print('Encrypting:', message)
        from pycloud.core.security import AESEncryption
        aes1 = AESEncryption()
        print('Using key:', aes1.get_key())
        ciphertext = aes1.encrypt(message, encode=True)

        print('ciphertext:', ciphertext)
        aes2 = AESEncryption(aes1.get_key())
        original = aes2.decrypt(ciphertext)
        print('{} == {}? {}'.format(message, original, original==message))

    def task(self, task=None, name=None, tags=None, env=None, summary=False):
        hosts = self.cloud.query({'name': name, 'tags': tags, 'env': env})
        if not hosts:
            print('No hosts found!')
            return False
        else:
            print('Found these hosts:')
            for host in hosts:
                print('\t', host)

        task = self.cloud.get_task(task)
        if task is None:
            print('No task with that name found')
            return False
        results = task.run(hosts)
        print(results)

    def create_task(self, task_type=None, task_name=None, options=None):
        cls = self.cloud._task_types.get(task_type)
        task = cls(task_name, **options)
        self.cloud._tasks[task_name] = task
        self.cloud._save()
        print('Created')

    def operation(self, operation=None, **kwargs):
        raise NotImplemented()

if __name__ == '__main__':
    CLIHandler().run_command(sys.argv[1:])
