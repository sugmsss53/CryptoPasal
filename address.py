from eth_utils import keccak

def eth_address(public_key):
    
    pub_bytes = public_key.to_bytes()
    addr = keccak(pub_bytes[1:])[-20:]
    return "0x" + addr.hex()
