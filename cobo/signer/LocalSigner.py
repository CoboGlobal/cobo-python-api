import hashlib

import ecdsa
from ecdsa import BadSignatureError
from ecdsa.util import sigencode_der, sigdecode_der

from cobo.signer.ApiSigner import ApiSigner


class LocalSigner(ApiSigner):

    def __init__(self, priv_key: str):
        secexp = int.from_bytes(bytes.fromhex(priv_key), 'big')
        self.key = ecdsa.SigningKey.from_secret_exponent(secexp, curve=ecdsa.SECP256k1)

    def sign(self, message: str) -> str:
        return self.key.sign(data=hashlib.sha256(message.encode()).digest(),
                             hashfunc=hashlib.sha256,
                             sigencode=sigencode_der).hex()

    @staticmethod
    def double_hash256(content):
        return hashlib.sha256(hashlib.sha256(content.encode()).digest()).digest()


def verify_ecdsa_signature(content: str, signature: str, pub_key: str):
    vk: ecdsa.VerifyingKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(pub_key),
                                                            hashfunc=hashlib.sha256,
                                                            curve=ecdsa.SECP256k1)
    try:
        return vk.verify(signature=bytes.fromhex(signature),
                         data=hashlib.sha256(content.encode()).digest(),
                         hashfunc=hashlib.sha256,
                         sigdecode=sigdecode_der)
    except BadSignatureError:
        return False


def generate_new_key():
    sk: ecdsa.SigningKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk: ecdsa.VerifyingKey = sk.verifying_key
    return sk.to_string().hex(), vk.to_string("compressed").hex()
