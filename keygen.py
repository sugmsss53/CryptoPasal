from eth_keys import keys
import hashlib

def generate_private_key(seed):
    """
    Derive a private key from the BIP-39 seed.
    Uses SHA-256 to compress the 64-byte seed into a 32-byte private key.
    The private key is a 256-bit number on the secp256k1 elliptic curve.
    """
    hashed = hashlib.sha256(seed).digest()
    return keys.PrivateKey(hashed)

def get_public_key(private_key):
    """
    Derive the public key from the private key.
    Uses elliptic curve multiplication on secp256k1.
    Safe to share — mathematically impossible to reverse back to private key.
    """
    return private_key.public_key
