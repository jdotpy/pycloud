from paramiko.agent import Agent
from paramiko.rsakey import RSAKey
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto import Random

import base64
import json
import stat
import os
import io
from base64 import b64encode

def generate_secret_key(length=128):
    random = os.urandom(length)
    key = b64encode(random).decode('utf-8')
    return key

def get_agent_keys():
    agent = Agent()
    keys = [KeyPair(_key=key) for key in agent.get_keys()]
    agent.close()
    return keys

class KeyPair():
    KEY_SIZE = 4096

    def __init__(self, private_key=None, private_key_path=None, _key=None, password=None):
        if private_key:
            self._key = RSAKey(file_obj=io.StringIO(private_key))
        elif private_key_path:
            self._key = RSAKey(filename=private_key_path, password=password)
        elif _key:
            self._key = _key
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

    def encrypt(self, data, encoding='utf-8', encode_payload=False):
        if isinstance(data, str) and encoding:
            data = data.encode(encoding)
        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        ciphertext = cipher.encrypt(data)
        if encode_payload:
            return base64.b64encode(ciphertext).decode('utf-8')
        else:
            return ciphertext

    def decrypt(self, ciphertext, encoding='utf-8'):
        if isinstance(ciphertext, str):
            ciphertext = base64.b64decode(ciphertext.encode('utf-8'))

        cipher = PKCS1_OAEP.new(self.as_pycrypto())
        data = cipher.decrypt(ciphertext)
        if encoding:
            text = data.decode(encoding)
        return text

    def to_file(self, path, password=None):
        self._key.write_private_key_file(path, password=password)

class DecryptionError(ValueError):
    pass

class AESEncryption():
    DEFAULT_KEY_SIZE = 32

    @classmethod
    def generate_key(cls, key_size=None):
        if key_size is None:
            key_size = cls.DEFAULT_KEY_SIZE

        key = Random.new().read(key_size)
        return base64.b64encode(key).decode('utf-8')

    def get_key(self):
        return base64.b64encode(self.key).decode('utf-8')

    def __init__(self, key=None, iv=None, encoding='utf-8'):
        if key is None:
            key = self.generate_key()
        if isinstance(key, str):
            key = base64.b64decode(key.encode('utf-8'))
        if iv is None:
            iv = Random.new().read(AES.block_size)
        self.iv = iv
        self.key = key
        self.encoding = encoding
        self.cipher = AES.new(self.key, AES.MODE_CFB, iv)

    def encrypt(self, content, encode=False):
        if self.encoding:
            content.encode(self.encoding)
        message = self.iv + self.cipher.encrypt(content)
        if encode:
            message = base64.b64encode(message).decode('utf-8')
        return message

    def decrypt(self, ciphertext):
        if isinstance(ciphertext, str):
            ciphertext = base64.b64decode(ciphertext.encode('utf-8'))
        message = self.cipher.decrypt(ciphertext)
        content = message[AES.block_size:]
        if self.encoding:
            content = content.decode(self.encoding)
        return content

class SecurityError(ValueError):
    pass
        
class PrivateFile():
    perm_mode = stat.S_IRUSR | stat.S_IWUSR  # This is octol 0o600
    umask = os.umask(0)

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.handler = None

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

    def read(self):
        if not self.handler:
            self.__enter__()
        return self.handler.read()

    def write(self, content):
        if not self.handler:
            self.__enter__()
        return self.handler.write(content)

    def close(self):
        self.handler.close()

    def __exit__(self, *args, **kwargs):
        self.close()

def make_private_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    return True

class AESEncryptedFile():
    def __init__(self, path, key, mode='rb', encoding='utf-8', constructor=open):
        self.path = path
        self.mode = mode
        self.key = key
        self.encoding = encoding
        self.constructor = constructor
        
        # Ensure we're working in binary here...
        if 'b' not in self.mode:
            self.mode += 'b'

    def __enter__(self):
        self.file_obj = self.constructor(self.path, self.mode)
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def read(self):
        data = self.file_obj.read()
        decrypted_data = AESEncryption(self.key, encoding=self.encoding).decrypt(data)
        return decrypted_data
        
    def write(self, content):
        encrypted_data = AESEncryption(self.key, encoding=self.encoding).encrypt(content)
        result = self.file_obj.write(encrypted_data)
        return result

    def close(self):
        self.file_obj.close()

class EncryptedJsonFile(AESEncryptedFile):
    def read(self):
        json_text = super(EncryptedJsonFile, self).read()
        return json.loads(json_text)
        
    def write(self, obj):
        json_text = json.dumps(obj)
        return super(EncryptedJsonFile, self).write(json_text)
