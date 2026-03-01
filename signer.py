import json
import os
from eth_account import Account
from eth_account.signers.local import LocalAccount

# Output path for signed transaction file
# VS Code / laptop testing : "signed_tx.json"
# Pi with pendrive          : "/mnt/usb/signed_tx.json"
SIGNED_TX_FILE = "signed_tx.json"

def sign_transaction(private_key_obj, tx_data: dict):
    """
    Sign a real Ethereum transaction using ECDSA (secp256k1 curve).

    tx_data must contain:
      - to       : recipient address (string, 0x...)
      - value    : amount in Wei (int)  — 1 ETH = 10^18 Wei
      - gas      : gas limit (int)      — 21000 for simple ETH transfer
      - gasPrice : gas price in Wei (int)
      - nonce    : account transaction count (int)
      - chainId  : network ID — 11155111=Sepolia testnet, 1=mainnet

    Returns a dict with rawTransaction hex ready for broadcasting.

    BUG FIXED: Now uses eth_account for proper RLP encoding.
    BUG FIXED: Original code passed dict to keccak() directly — crash fixed.
    """
    # Extract raw 32-byte private key from eth_keys object
    raw_key = private_key_obj.to_bytes()

    # Create eth_account compatible signer
    account: LocalAccount = Account.from_key(raw_key)

    # Checksum the to address — eth_account requires EIP-55 checksum format
    # All-lowercase addresses are rejected even if technically valid
    from web3 import Web3
    tx_data["to"] = Web3.to_checksum_address(tx_data["to"])

    # Sign transaction — ECDSA with secp256k1
    signed = account.sign_transaction(tx_data)

    return {
        "from"          : account.address,
        "to"            : tx_data["to"],
        "value_eth"     : tx_data["value"] / 10**18,
        "gas"           : tx_data["gas"],
        "gasPrice_gwei" : tx_data["gasPrice"] / 10**9,
        "nonce"         : tx_data["nonce"],
        "chainId"       : tx_data["chainId"],
        "rawTransaction": signed.raw_transaction.hex(),
        "txHash"        : signed.hash.hex(),
    }

def save_signed_tx(signed_tx: dict, output_path: str = SIGNED_TX_FILE):
    """
    Save signed transaction to JSON file.
    On Pi  → saves to pendrive so laptop can pick it up and broadcast.
    Laptop → saves locally for testing.
    """
    with open(output_path, "w") as f:
        json.dump(signed_tx, f, indent=2)
    print(f"\nSigned transaction saved to: {output_path}")

def load_signed_tx(file_path: str = SIGNED_TX_FILE) -> dict:
    """
    Load signed transaction from JSON file.
    Called by broadcast_tx.py on the laptop.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Signed transaction file not found: {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)