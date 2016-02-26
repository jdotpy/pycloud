from ..core.cloud import Cloud
from ..core.security import generate_secret_key, KeyPair, PrivateFile
from .datasource import JsonDataSource
import os
import errno
import yaml

def new_cloud(path, name='Anonymous'):
    if path_exists(path):
        raise ValueError('Path Already Exists!')
    key = KeyPair()
    datasource_path = path + '/data.json'
    config = {
        'name': name,
        'datasource': datasource_path,
        'secret_key': generate_secret_key(),
        'private_key': key.private_key_str()
    }
    create_project(path, config)
    cloud = Cloud(config, datasource=JsonDataSource(datasource_path))
    cloud.datasource._save(key)

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
    with PrivateFile(path + '/' + 'config.yaml', 'w') as f:
        f.write(yaml.dump(config))
    os.makedirs(path + '/' + 'data.yaml')
