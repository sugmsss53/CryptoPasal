import os


def generate_entropy():
    # Pull 32 bytes (256 bits) from the OS random source.
    # On Linux/Pi this reads from /dev/urandom which is seeded
    # by hardware events, so it is safe to use for key material.
    return os.urandom(32)
