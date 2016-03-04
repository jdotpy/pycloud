from .cloud import LocalCloud
from ..core.security import generate_secret_key, KeyPair, PrivateFile, EncryptedJsonFile, make_private_dir, AESEncryption
import os
import errno
import yaml

def new_cloud(path, name='My Cloud', key_path=None):
    if path_exists(path):
        raise ValueError('Path Already Exists!')

    secret_key = AESEncryption.generate_key()
    path = os.path.abspath(path)
    make_private_dir(path)
    config_file_path = os.path.join(path, 'config.yaml')
    data_file_path = os.path.join(path, 'data.json')
    default_key_path = os.path.join(path, LocalCloud.DEFAULT_KEY_NAME + '.key')

    if key_path:
        key_obj = KeyPair(private_key_path=key_path)
    else:
        key_obj = KeyPair()
    key_obj.to_file(default_key_path, secret_key)

    config = {
        'name': name,
        'datasource': data_file_path,
        'secret_key': secret_key,
        'keys': {
            LocalCloud.DEFAULT_KEY_NAME: {'private_key_path': default_key_path}
        }
    }

    with PrivateFile(config_file_path, 'w') as f:
        f.write(yaml.dump(config))
    with EncryptedJsonFile(data_file_path, secret_key, 'w', constructor=PrivateFile) as f:
        f.write({})

    cloud = LocalCloud(config=config)
    cloud._save()

def path_exists(path):
    return os.path.exists(path)
