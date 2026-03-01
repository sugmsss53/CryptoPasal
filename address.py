from eth_utils import keccak


def eth_address(public_key):
    # Drop the 0x04 prefix byte, hash the remaining 64 bytes with Keccak-256,
    # then keep only the last 20 bytes — that is the Ethereum address.
    pub_bytes = public_key.to_bytes()
    addr = keccak(pub_bytes[1:])[-20:]
    return "0x" + addr.hex()
