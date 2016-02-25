from paramiko.rsakey import RSAKey
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from os import urandom
import io
from base64 import b64encode

def generate_secret_key(length=128):
    random = urandom(length)
    key = b64encode(random).decode('utf-8')
    return key

class KeyPair():
    KEY_SIZE = 4096

    def __init__(self, source=None):
        if source is None:
            self._key = RSAKey.generate(self.KEY_SIZE)
        elif isinstance(source, str):
            self._key = RSAKey(file_obj=io.StringIO(source))
        else:
            raise ValueError('Unsupported key source')

    def public_key_str(self):
        return self._key.get_base64()

    def private_key_str(self):
        buf = io.StringIO()
        self._key.write_private_key(buf)
        buf.seek(0)
        private = buf.read()
        return private

    def get_keypair_str(self):
        return self.public_key_str(), self.private_key_str()

    def as_paramiko(self):
        return self._key

    def as_pycrypto(self):
        return RSA.importKey(self.private_key_str())

    def encrypt(self, text):
        text_bytes = text.encode('utf-8')
        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        ciphertext = cipher.encrypt(text_bytes)
        return ciphertext

    def decrypt(self, ciphertext):
        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        text_bytes = cipher.decrypt(ciphertext)
        text = text_bytes.decode('utf-8')
        return text
        
