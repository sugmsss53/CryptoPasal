import os
from cryptography.fernet import Fernet
from eth_keys import keys


WALLET_FILE = "wallet.enc"
KEY_FILE    = "secret.key"


def _load_or_create_key():
    # If a key file already exists, load it.
    # Otherwise generate a fresh one and save it.
    # secret.key must be kept private — losing it means losing access
    # to the encrypted wallet.
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def store_wallet(private_key):
    # Grab the raw 32 private key bytes, encrypt them with
    # AES-128-CBC + HMAC-SHA256 (Fernet), then write to disk.
    # Storing raw bytes (not a pickled object) keeps it portable.
    key = _load_or_create_key()
    f   = Fernet(key)
    encrypted = f.encrypt(private_key.to_bytes())
    with open(WALLET_FILE, "wb") as wf:
        wf.write(encrypted)


def load_wallet():
    # Read and decrypt the key file. Fernet will raise InvalidToken
    # if the ciphertext has been tampered with, so corruption is caught.
    if not os.path.exists(WALLET_FILE):
        return None
    key = _load_or_create_key()
    f   = Fernet(key)
    with open(WALLET_FILE, "rb") as wf:
        encrypted = wf.read()
    raw_bytes = f.decrypt(encrypted)
    return keys.PrivateKey(raw_bytes)
