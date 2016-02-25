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
    NO_CLOUD_COMMANDS = ['init', 'help', 'encrypt']
    COMMANDS = {
        # command name, function
        'help': {
            'func': 'help'
        },
        'info': {
            'func': 'info'
        },
        'init': {
            'func': 'init'
        },
        'ssh': {
            'func': 'ssh'
        },
        'encrypt': {
            'func': 'encrypt'
        }
    }

    def __init__(self):
        self.cloud = None

    def run_command_str(self, text):
        args = parser.parse_args(shlex.split(text))
        self.run_command(args)

    def run_command(self, args):
        options = self._parse_args(args)
        command_parts = options['commands']
        command_name, args = command_parts[0], command_parts[1:]
        if self.cloud is None and command_name not in self.NO_CLOUD_COMMANDS:
            self.cloud = self._setup_cloud(options)
    
        if command_name not in self.COMMANDS:
            command_name = 'help'
            args.insert(0, command_name)

        command = self.COMMANDS[command_name]
        func = getattr(self, command['func'])
        func(*args)

    def _setup_cloud(self, options):
        config_file = options['config']
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
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('commands', nargs="+", metavar="cmd")
        parser.add_argument('--config', required=False, default=None)
        options = parser.parse_args(args)
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

    def encrypt(self, *args):
        text = 'my text'
        key = KeyPair()
        ciphertext = key.encrypt(text)
        decrypted_text = key.decrypt(ciphertext)
        print('Plain: "{}" \nCiphertext: "{}" \nDecrypted: "{}"'.format(text, ciphertext, decrypted_text))

if __name__ == '__main__':
    CLIHandler().run_command(sys.argv[1:])
