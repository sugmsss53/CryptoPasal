from mnemonic import Mnemonic
from entropy import generate_entropy

def generate_mnemonic():
    """
    Generate a 24-word BIP-39 mnemonic seed phrase.
    Uses 256 bits of secure entropy as the source.
    This is the human-readable backup of your entire wallet.
    """
    mnemo = Mnemonic("english")
    entropy = generate_entropy()
    words = mnemo.to_mnemonic(entropy)
    return words

def mnemonic_to_seed(words):
    """
    Convert a BIP-39 mnemonic phrase into a 64-byte seed.
    Uses PBKDF2-HMAC-SHA512 with 2048 iterations internally.
    This seed is used to derive the private key.
    """
    mnemo = Mnemonic("english")
    return mnemo.to_seed(words)
