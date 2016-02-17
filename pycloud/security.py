from paramiko.rsakey import RSAKey
from os import urandom
import io

def generate_secret_key(length=128)
    random = urandom(length)
    key = b64encode(random).decode('utf-8')
    return token

class KeyPair():
    KEY_SIZE = 4096

    def __init__(self, source=None):
        if source is None:
            self._key = RSAKey.generate(self.KEY_SIZE)
        else:
            raise ValueError('Unsupported key source')

    def public_key_str(self):
        return self._key.get_base64()

    def private_key_str(self):
        buf = io.StringIO()
        key.write_private_key(buf)
        private = buf.read()
        return self._key

    def get_keypair_str(self):
        return self.public_key_str(), self.private_key_str()

    def as_paramiko(self):
        return self._key
