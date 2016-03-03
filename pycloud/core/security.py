from paramiko.rsakey import RSAKey
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import json
import stat
import os
import io
from base64 import b64encode

def generate_secret_key(length=128):
    random = os.urandom(length)
    key = b64encode(random).decode('utf-8')
    return key

class KeyPair():
    KEY_SIZE = 4096

    def __init__(self, private_key=None, private_key_path=None):
        if private_key:
            self._key = RSAKey(file_obj=io.StringIO(private_key))
        elif private_key_path:
            self._key = RSAKey(filename=private_key_path)
        else:
            self._key = RSAKey.generate(self.KEY_SIZE)

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

    def encrypt(self, data, encoding='utf-8'):
        if isinstance(data, str) and encoding:
            data = data.encode(encoding)
        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        ciphertext = cipher.encrypt(data)
        return ciphertext

    def decrypt(self, ciphertext, encoding='utf-8'):
        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        data = cipher.decrypt(ciphertext)
        if encoding:
            text = data.decode(encoding)
        return text

class SecurityError(ValueError):
    pass
        
class PrivateFile():
    perm_mode = stat.S_IRUSR | stat.S_IWUSR  # This is octol 0o600
    umask = os.umask(0)

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode

    def __enter__(self):
        try:
            stat = os.stat(self.path)
        except FileNotFoundError:
            stat = None
        if stat:
            others_perm = oct(stat.st_mode)[-2:]
            if others_perm != '00':
                raise SecurityError('Insecure Operation. File {} is not private'.format(self.path))
        if 'w' in self.mode:
            self.handler = os.fdopen(os.open(self.path, os.O_WRONLY | os.O_CREAT, self.perm_mode), self.mode)
            return self.handler
        else:
            self.handler = open(self.path, self.mode)
            return self.handler

    def __exit__(self, *args, **kwargs):
        self.handler.close()

class RSAEncryptedFile():
    def __init__(self, path, key, mode='rb', encoding='utf-8'):
        self.path = path
        self.mode = mode
        self.key = key
        self.encoding = encoding
        
        # Ensure we're working in binary here...
        if 'b' not in self.mode:
            self.mode += 'b'

    def __enter__(self):
        self.file_obj = open(self.path, self.mode)
        return self

    def __exit__(self, *args, **kwargs):
        self.file_obj.close()

    def read(self):
        data = self.file_obj.read()
        decrypted_data = self.key.decrypt(data, encoding=self.encoding)
        return decrypted_data
        
    def write(self, content):
        encrypted_data = self.key.encrypt(content, encoding=self.encoding)
        result = self.file_obj.write(encrypted_data)
        return result

class EncryptedJsonFile(RSAEncryptedFile):
    def read(self):
        json_text = super(EncryptedJsonFile, self).read()
        return json.loads(json_text)
        
    def write(self, obj):
        json_text = json.dumps(obj)
        return super(EncryptedJsonFile, self).write(json_text)
