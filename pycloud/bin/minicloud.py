#!/usr/bin/env python

from quickconfig import Configuration
from pycloud.minicloud.utils import new_cloud, path_exists
from pycloud.minicloud.datasource import JsonDataSource
from pycloud.core.cloud import Cloud, Host
from pycloud.core.net import SSHGroup
from pycloud.core.security import *
import argparse
import shlex
import sys

class CLIHandler():
    DEFAULT_CONFIG_SOURCES = [
        '/etc/pycloud.yaml',
        '~/.pycloud.yaml',
        'config.yaml'
    ]
    NO_CLOUD_COMMANDS = ['init', 'help', 'encrypt', 'file']
    COMMANDS = {
        # command name, function
        'info': {
            'func': 'info'
        },
        'init': {
            'func': 'init'
        },
        'ssh': {
            'func': 'ssh'
        },
        'register': {
            'func': 'register',
            'args': {
                'hostname': {},
                ('-n','--name'): {},
                ('-e','--env'): {},
                ('-e','--env'): {},
                ('-t','--tags'): {'nargs': '*'},
            }
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

        if self.cloud is None and command_name not in self.NO_CLOUD_COMMANDS:
            self.cloud = self._setup_cloud(options.pop('config'))
    
        command = self.COMMANDS[command_name]
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
        datasource = JsonDataSource(data_path)
        try:
            cloud = Cloud(config, datasource=datasource)
        except ValueError as e:
            cloud = None
            print('Could not configure cloud', e)
        datasource._load(cloud.key)
        return cloud

    def _parse_args(self, args):
        root_parser = argparse.ArgumentParser(description='Mini cloud!')
        subparsers = root_parser.add_subparsers(dest='command')
        for cmd_name, cmd_info in self.COMMANDS.items():
            cmd_parser = subparsers.add_parser(cmd_name)
            cmd_parser.add_argument('--config', default=None)
            for cmd_args, cmd_options in cmd_info.get('args', {}).items():
                if isinstance(cmd_args, str):
                    cmd_args = [cmd_args]
                cmd_parser.add_argument(*cmd_args, **cmd_options)
        options = root_parser.parse_args(args)
        return vars(options)

    def init(self, path):
        if path_exists(path):
            print('Path already exists')
            return False

        name = input('What would you like the project to be called? ')
        new_cloud(path, name=name)

    def help(self, *args):
        print('help you? no. Not even with:', args)

    def info(self):
        print('Pycloud initialized: ', self.cloud)
        print(self.cloud.datasource)
        print('{} hosts found'.format(len(self.cloud.datasource.hosts)))

    def ssh(self, *args):
        group = SSHGroup([], max_pool_size=2)
        group.run_command('for i in {1..5}; do echo "$i";sleep 1; done')

    def register(self, hostname=None, name=None, tags=None, env='default', *args, **kwargs):
        """ Register a new host """
        if name is None:
            name = hostname
        print('Registring host [{}] {} ({}) (Tags: {})'.format(
            env, name, hostname, tags
        ))

if __name__ == '__main__':
    CLIHandler().run_command(sys.argv[1:])
