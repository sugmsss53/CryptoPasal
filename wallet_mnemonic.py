from mnemonic import Mnemonic
from entropy import generate_entropy


def generate_mnemonic():
    # Turn the raw entropy into a 24-word BIP-39 phrase.
    # Each word encodes 11 bits, so 24 words covers 256 bits + checksum.
    mnemo = Mnemonic("english")
    entropy = generate_entropy()
    return mnemo.to_mnemonic(entropy)


def mnemonic_to_seed(words):
    # Stretch the phrase into a 64-byte seed with PBKDF2-HMAC-SHA512.
    # 2048 rounds of hashing make brute-force guessing impractical.
    mnemo = Mnemonic("english")
    return mnemo.to_seed(words)
