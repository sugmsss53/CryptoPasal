import os

def generate_entropy():
    """
    Generate 256 bits of cryptographically secure random entropy.
    Uses the operating system's secure random number generator (CSPRNG).
    This is the starting point for all wallet key generation.
    """
    return os.urandom(32)
