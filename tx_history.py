import json
import os
import hashlib
from datetime import datetime

HISTORY_FILE = "tx_history.json"

def _hash_entry(entry: dict) -> str:
    """
    Compute SHA-256 hash of a transaction entry.
    This is used to chain entries together — same concept as blockchain.
    If any entry is changed, its hash changes and breaks all entries after it.
    """
    entry_str = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(entry_str.encode()).hexdigest()

def _load_history() -> list:
    """Load existing transaction history from file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def _save_history(history: list):
    """Save transaction history to file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def log_transaction(from_address: str, to_address: str,
                    amount: float, tx_hash: str, signature: str):
    """
    Log a signed transaction with hash chaining for tamper detection.

    Each entry contains:
      - Transaction details (from, to, amount)
      - Cryptographic signature
      - Hash of this entry
      - Hash of previous entry (the chain link)

    This creates a tamper-evident log:
      Entry 1 hash ──→ stored in Entry 2
      Entry 2 hash ──→ stored in Entry 3
      ...
    If anyone edits Entry 1, its hash changes,
    which breaks Entry 2, which breaks Entry 3, etc.
    Tampering is immediately detectable.
    """
    history = _load_history()

    # Get previous entry hash for chaining
    prev_hash = history[-1]["entry_hash"] if history else "0" * 64

    # Build entry (without hash first)
    entry = {
        "index"      : len(history) + 1,
        "timestamp"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from"       : from_address,
        "to"         : to_address,
        "amount_eth" : amount,
        "tx_hash"    : tx_hash,
        "signature"  : signature,
        "prev_hash"  : prev_hash,
    }

    # Add hash of this entry (includes prev_hash — this is the chain)
    entry["entry_hash"] = _hash_entry(entry)

    history.append(entry)
    _save_history(history)
    print(f"\nTransaction logged. Entry #{entry['index']} | Hash: {entry['entry_hash'][:16]}...")

def show_history():
    """
    Display all transactions and verify chain integrity.
    Detects if any record has been tampered with.
    """
    history = _load_history()

    if not history:
        print("\nNo transaction history found.")
        return

    print("\n" + "=" * 60)
    print("           TRANSACTION HISTORY")
    print("=" * 60)

    prev_hash  = "0" * 64
    chain_ok   = True

    for entry in history:
        print(f"\n  Transaction #{entry['index']}")
        print(f"  Time      : {entry['timestamp']}")
        print(f"  From      : {entry['from']}")
        print(f"  To        : {entry['to']}")
        print(f"  Amount    : {entry['amount_eth']} ETH")
        print(f"  TX Hash   : {entry['tx_hash'][:24]}...")
        print(f"  Prev Hash : {entry['prev_hash'][:24]}...")
        print(f"  Entry Hash: {entry['entry_hash'][:24]}...")

        # Verify chain integrity by recomputing hash
        stored_hash  = entry["entry_hash"]
        entry_to_check = {k: v for k, v in entry.items() if k != "entry_hash"}
        recomputed   = _hash_entry({**entry_to_check, "entry_hash": stored_hash})

        if recomputed != stored_hash or entry["prev_hash"] != prev_hash:
            print(f"  WARNING: Entry #{entry['index']} TAMPERED!")
            chain_ok = False

        prev_hash = stored_hash
        print("  " + "-" * 52)

    print("\n" + "=" * 60)
    if chain_ok:
        print("  Chain integrity verified — no tampering detected.")
    else:
        print("  CHAIN INTEGRITY FAILED — history may be tampered!")
    print("=" * 60 + "\n")

def get_tx_count() -> int:
    """Return total number of logged transactions."""
    return len(_load_history())
