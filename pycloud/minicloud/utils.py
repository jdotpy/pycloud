from ..core.cloud import Cloud
from ..core.security import generate_secret_key, KeyPair
import os
import errno
import yaml

def new_cloud(name='Anonymous'):
    config = {
        'name': name,
        'secret_key': generate_secret_key(),
    }
    cloud = Cloud(config)
    cloud.set_default_credentials('pycloud', '')

def path_exists(path):
    return os.path.exists(path)

def create_project(path, config):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    with open(path + '/' + 'pycloud.yaml', 'w') as f:
        f.write(yaml.dump(config))
