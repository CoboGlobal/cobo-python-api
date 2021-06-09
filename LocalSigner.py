import hashlib
from binascii import a2b_hex, b2a_hex

from pycoin.encoding import from_bytes_32, to_bytes_32, public_pair_to_sec
from pycoin.key import Key
import secrets

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

    @staticmethod
    def generate_new_key():
        secret = secrets.randbits(256)
        priv_key = b2a_hex(to_bytes_32(secret)).decode()
        key = Key(secret_exponent=secret)
        pub_key = public_pair_to_sec(key.public_pair())
        return priv_key, b2a_hex(pub_key).decode()

_secret, _key = LocalSigner.generate_new_key()
print("API_SECRET: %s" % _secret)
print("API_KEY: %s" % _key)

