import json
import os
import hashlib
from datetime import datetime


HISTORY_FILE = "tx_history.json"


def _hash_entry(entry: dict) -> str:
    # Serialize the entry with sorted keys so the output is always
    # identical regardless of insertion order, then SHA-256 it.
    entry_str = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(entry_str.encode()).hexdigest()


def _load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def _save_history(history: list):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def log_transaction(from_address, to_address, amount, tx_hash, signature):
    history = _load_history()

    # Each entry stores the hash of the previous entry.
    # Changing any old record breaks its hash, which then breaks
    # every entry that comes after it — tamper is immediately visible.
    prev_hash = history[-1]["entry_hash"] if history else "0" * 64

    entry = {
        "index"     : len(history) + 1,
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from"      : from_address,
        "to"        : to_address,
        "amount_eth": amount,
        "tx_hash"   : tx_hash,
        "signature" : signature,
        "prev_hash" : prev_hash,
    }

    entry["entry_hash"] = _hash_entry(entry)
    history.append(entry)
    _save_history(history)
    print(f"\nLogged entry #{entry['index']} | {entry['entry_hash'][:16]}...")


def show_history():
    history = _load_history()
    if not history:
        print("\nNo transactions recorded yet.")
        return

    print("\n" + "=" * 60)
    print("           TRANSACTION HISTORY")
    print("=" * 60)

    prev_hash = "0" * 64
    chain_ok  = True

    for entry in history:
        print(f"\n  #{entry['index']}  {entry['timestamp']}")
        print(f"  From : {entry['from']}")
        print(f"  To   : {entry['to']}")
        print(f"  Value: {entry['amount_eth']} ETH (simulated)")
        print(f"  Hash : {entry['entry_hash'][:32]}...")

        # Recompute the hash and compare. Any mismatch means the
        # record or the chain link was modified after it was written.
        stored = entry["entry_hash"]
        check  = {k: v for k, v in entry.items() if k != "entry_hash"}
        recomputed = _hash_entry({**check, "entry_hash": stored})

        if recomputed != stored or entry["prev_hash"] != prev_hash:
            print(f"  *** WARNING: entry #{entry['index']} has been tampered with ***")
            chain_ok = False

        prev_hash = stored
        print("  " + "-" * 52)

    print("\n" + "=" * 60)
    if chain_ok:
        print("  All entries verified — chain intact.")
    else:
        print("  INTEGRITY CHECK FAILED — one or more records modified.")
    print("=" * 60 + "\n")


def get_tx_count() -> int:
    return len(_load_history())
