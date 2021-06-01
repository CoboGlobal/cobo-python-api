import hashlib
from binascii import a2b_hex, b2a_hex

from pycoin.encoding import from_bytes_32
from pycoin.key import Key

from ApiSigner import ApiSigner


class LocalSigner(ApiSigner):

    def __init__(self, priv_key):
        self.key = Key(secret_exponent=from_bytes_32(a2b_hex(priv_key)))

    def sign(self, message):
        return b2a_hex(self.key.sign(self.double_hash256(message))).decode()

    @staticmethod
    def double_hash256(content):
        return hashlib.sha256(hashlib.sha256(content.encode()).digest()).digest()

    @staticmethod
    def verify(content, signature, pub_key):
        key = Key.from_sec(a2b_hex(pub_key))
        return key.verify(LocalSigner.double_hash256(content), a2b_hex(signature))
