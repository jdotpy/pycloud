#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pycloud',
    version='0.1',
    description='SSH Tools for server management.',
    author='KJ',
    author_email='<redacted>',
    url='<TBD>',
    packages=[
        'pycloud',
        'pycloud.core',
        'pycloud.minicloud',
        'pycloud.web',
    ],
    install_requires=[
        'paramiko',
        'requests',
        'pyyaml',
        'quickconfig'
    ],
    scripts=[
        'pycloud/bin/minicloud.py',
        'pycloud/bin/pycloudctrl.py',
        'pycloud/bin/web.py',
    ],
)
