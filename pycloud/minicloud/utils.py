from .cloud import LocalCloud
from ..core.security import generate_secret_key, KeyPair, PrivateFile, EncryptedJsonFile
import os
import errno
import yaml

def new_cloud(path, name='My Cloud', key_path=None):
    path = os.path.abspath(path)
    print('New cloud creation at:', path)
    if path_exists(path):
        raise ValueError('Path Already Exists!')
    if not key_path:
        key = {'private_key': KeyPair().private_key_str()}
    else:
        key = {'private_key_path': key_path}
    key_obj = KeyPair(**key)

    datasource_path = path + '/data.json'
    config = {
        'name': name,
        'datasource': datasource_path,
        'secret_key': generate_secret_key(),
        'keys': {
            LocalCloud.DEFAULT_KEY_NAME: key 
        }
    }
    create_project(path, config, key=key_obj)
    cloud = LocalCloud(datasource_path, config=config)
    cloud._save()

def path_exists(path):
    return os.path.exists(path)

def create_project(path, config, key):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    config_file_path = path + '/' + 'config.yaml' 
    data_file_path = path + '/' + 'data.json'
    with PrivateFile(config_file_path, 'w') as f:
        f.write(yaml.dump(config))
    with EncryptedJsonFile(data_file_path, key, 'w') as f:
        f.write({})
