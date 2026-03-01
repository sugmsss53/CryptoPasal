import os
from cryptography.fernet import Fernet
from eth_keys import keys

WALLET_FILE = "wallet.enc"
KEY_FILE    = "secret.key"

def generate_key():
    """
    Load existing AES encryption key or generate a new one.
    Key is stored in secret.key file.
    NEVER share this file — it is used to decrypt your private key.
    """
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def store_wallet(private_key):
    """
    Encrypt and store the private key securely using AES (Fernet).

    Steps:
      1. Load or generate AES encryption key
      2. Extract raw 32 bytes from private key object
      3. Encrypt with Fernet (AES-128-CBC + HMAC-SHA256)
      4. Save encrypted bytes to wallet.enc

    BUG FIXED: Uses raw bytes instead of pickle (safer + portable)
    BUG FIXED: Renamed fernet_obj to avoid variable shadowing
    """
    key = generate_key()
    fernet_obj = Fernet(key)
    raw_bytes = private_key.to_bytes()
    encrypted = fernet_obj.encrypt(raw_bytes)
    with open(WALLET_FILE, "wb") as wallet_file:
        wallet_file.write(encrypted)

def load_wallet():
    """
    Load and decrypt the private key from wallet.enc.
    Requires secret.key to be present in the same folder.
    """
    if not os.path.exists(WALLET_FILE):
        return None
    key = generate_key()
    fernet_obj = Fernet(key)
    with open(WALLET_FILE, "rb") as wallet_file:
        encrypted = wallet_file.read()
    raw_bytes = fernet_obj.decrypt(encrypted)
    return keys.PrivateKey(raw_bytes)
