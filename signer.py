import json
import os
from eth_account import Account
from web3 import Web3


SIGNED_TX_FILE = "signed_tx.json"


def sign_transaction(private_key_obj, tx_data: dict) -> dict:
    # eth_account needs the raw 32-byte key, not the eth_keys wrapper.
    raw_key = private_key_obj.to_bytes()
    account = Account.from_key(raw_key)

    # eth_account requires the recipient to be in EIP-55 checksum format.
    tx_data["to"] = Web3.to_checksum_address(tx_data["to"])

    # ECDSA sign — this produces r, s, v and the RLP-encoded raw transaction.
    signed = account.sign_transaction(tx_data)

    return {
        "from"          : account.address,
        "to"            : tx_data["to"],
        "value_eth"     : tx_data["value"] / 10 ** 18,
        "gas"           : tx_data["gas"],
        "gasPrice_gwei" : tx_data["gasPrice"] / 10 ** 9,
        "nonce"         : tx_data["nonce"],
        "chainId"       : tx_data["chainId"],
        "rawTransaction": signed.raw_transaction.hex(),
        "txHash"        : signed.hash.hex(),
    }


def save_signed_tx(signed_tx: dict, output_path: str = SIGNED_TX_FILE):
    # Write the signed transaction to a JSON file so it can be
    # transferred off the device and submitted to the network later.
    with open(output_path, "w") as f:
        json.dump(signed_tx, f, indent=2)
    print(f"\nSigned transaction saved to: {output_path}")


def load_signed_tx(file_path: str = SIGNED_TX_FILE) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)
