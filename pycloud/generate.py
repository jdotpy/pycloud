from .cloud import PyCloud
from .security import generate_secret_key, KeyPair

from base64 import b64encode

def new_cloud(name='my_cloud'):
    config = {
        'name': name,
        'secret_key': generate_secret_key(),
        'key': KeyPair().get_keypair_string()
    }
    return PyCloud(config)
