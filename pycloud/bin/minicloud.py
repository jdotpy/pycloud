#!/usr/bin/env python

from quickconfig import Configuration
from pycloud.minicloud.utils import new_cloud, path_exists
from pycloud.minicloud.cloud import LocalCloud
from pycloud.core.cloud import Host
from pycloud.core.net import SSHGroup
from pycloud.core.security import *
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
        'info': {
            'func': 'info',
        },
        'init': {
            'func': 'init',
            'cloud': False,
            'args': {
                'path': {'help': 'Path to new cloud dir'},
                ('-k', '--key'): {'help': 'Path to key to use as default'},
                ('-n', '--name'): {'help': 'Name of cloud'}
            }
        },
        'ssh': {
            'func': 'ssh',
            'args': {
                'ssh_command': {'help': 'Command to run'},
                ('-n','--name'): {},
                ('-e','--env'): {},
                ('-t','--tags'): {'nargs': '*'},
                ('--summary'): {'action': 'store_true', 'default': False}
            }
        },
        'register': {
            'func': 'register',
            'args': {
                'hostname': {},
                ('-n','--name'): {},
                ('-e','--env'): {},
                ('-e','--env'): {},
                ('-t','--tags'): {'nargs': '*'},
                ('-u','--user'): {},
                ('-p','--password'): {},
                ('-P','--ask-for-pass'): {'dest': 'ask_for_pass', 'action': 'store_true', 'default': False},
            }
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
    
        func = getattr(self, command['func'])
        func(**options)

    def _setup_cloud(self, config_file=None):
        if config_file:
            sources = [config_file]
        else:
            sources = self.DEFAULT_CONFIG_SOURCES
        config = Configuration(*sources)
        data_path = config.get('datasource')
        if data_path is None:
            raise ValueError('No valid configuration found!')
        cloud = LocalCloud(data_path, config=config)
        try:
            cloud = LocalCloud(data_path, config=config)
        except ValueError as e:
            cloud = None
            raise ValueError('Could not configure cloud: ' +  str(e))
        return cloud

    def _parse_args(self, args):
        root_parser = argparse.ArgumentParser(description='Mini cloud!')
        subparsers = root_parser.add_subparsers(dest='command')
        for cmd_name, cmd_info in self.COMMANDS.items():
            cmd_parser = subparsers.add_parser(cmd_name)
            if cmd_info.get('cloud', True):
                cmd_parser.add_argument('--config', default=None)
            for cmd_args, cmd_options in cmd_info.get('args', {}).items():
                if isinstance(cmd_args, str):
                    cmd_args = [cmd_args]
                cmd_parser.add_argument(*cmd_args, **cmd_options)
        options = root_parser.parse_args(args)
        return vars(options)

    def init(self, path=None, name=None, key=None):
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

        group = SSHGroup(hosts, max_pool_size=10)
        results = group.run_command(ssh_command)

        show_stdout = True
        show_stderr = not summary
        print(results.display(show_stderr=show_stderr, show_stdout=show_stdout))

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
        print(results)
        if results.success():
            print('Connection test successful. Saving host.')
            add = True
        else:
            add_anyway = input('Connection test failed. Save host anyway? (y/n): ')
            if add_anyway != 'y':
                return False
        self.cloud._hosts.append(host)
        self.cloud._save()

if __name__ == '__main__':
    CLIHandler().run_command(sys.argv[1:])
