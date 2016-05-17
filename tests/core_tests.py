import unittest
import base64

from pycloud.core.security import KeyPair
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

class KeyPairTests(unittest.TestCase):
    def test_keypair(self):
        keypair = KeyPair()
        c_key = RSA.importKey(key.public_key_str())
