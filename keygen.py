import hashlib
from eth_keys import keys


def generate_private_key(seed):
    # The secp256k1 private key must be exactly 32 bytes.
    # SHA-256 the 64-byte PBKDF2 seed to bring it down to size.
    hashed = hashlib.sha256(seed).digest()
    return keys.PrivateKey(hashed)


def get_public_key(private_key):
    # Public key is derived by multiplying the private key scalar
    # by the secp256k1 generator point G. There is no known way
    # to reverse this and recover the private key.
    return private_key.public_key
