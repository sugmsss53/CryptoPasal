import os
import json

from wallet_mnemonic import generate_mnemonic, mnemonic_to_seed
from keygen import generate_private_key
from address import eth_address
from signer import sign_transaction, save_signed_tx
from storage import store_wallet, load_wallet
from ui_mock import confirm_transaction, display_wallet_info
from qr_display import generate_qr
from tx_history import log_transaction, show_history, get_tx_count


WALLET_FILE      = "wallet.enc"
BALANCES_FILE    = "balances.json"
SIGNED_TX_OUTPUT = "signed_tx.json"


# All amounts in this tool are simulated — no real funds are moved.
CHAIN_ID = 11155111

AUTH_NICKNAME = "bojack"

# ------------------------------------------------------------------


def _load_balances():
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_balances(balances):
    with open(BALANCES_FILE, "w") as f:
        json.dump(balances, f, indent=2)


def get_balance(address):
    return _load_balances().get(address, 10.0)


def update_balance(address, new_balance):
    balances = _load_balances()
    balances[address] = round(new_balance, 6)
    _save_balances(balances)


# ------------------------------------------------------------------
# Wallet creation
# ------------------------------------------------------------------

def create_wallet():
    mnemonic = generate_mnemonic()
    words    = mnemonic.split()

    print("\n" + "=" * 52)
    print("   YOUR SEED PHRASE  —  24 WORDS")
    print("=" * 52)
    for i, word in enumerate(words, 1):
        print(f"   {i:2}. {word}")
    print("=" * 52)
    print("   Write this down on paper and store it safely.")
    print("   It will not be shown again.")
    print("=" * 52 + "\n")

    seed        = mnemonic_to_seed(mnemonic)
    private_key = generate_private_key(seed)
    public_key  = private_key.public_key
    address     = eth_address(public_key)

    store_wallet(private_key)

    print("Wallet saved (AES encrypted).")
    print(f"\nAddress : {address}")
    print(f"Balance : {get_balance(address)} ETH (simulated)\n")

    generate_qr(address, title="YOUR WALLET ADDRESS")

    return address, private_key


# ------------------------------------------------------------------
# Transaction signing
# ------------------------------------------------------------------

def sign_tx(wallet_address, private_key):
    print("\n--- SIGN TRANSACTION ---")

    # Recipient address validation
    to_address = input("Recipient address (0x...): ").strip()

    if not to_address.startswith("0x"):
        print("Address must start with 0x.")
        return
    if len(to_address) != 42:
        print(f"Address must be 42 characters. Got {len(to_address)}.")
        return
    try:
        int(to_address[2:], 16)
    except ValueError:
        print("Address contains non-hex characters.")
        return

    # EIP-55 checksum — eth_account rejects non-checksummed addresses
    from web3 import Web3
    to_address = Web3.to_checksum_address(to_address)

    # Amount
    try:
        amount = float(input("Amount (ETH, simulated): "))
    except ValueError:
        print("Enter a valid number.")
        return

    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    balance = get_balance(wallet_address)
    if amount > balance:
        print(f"Not enough balance. Current: {balance} ETH (simulated)")
        return

    # Nonce
    try:
        nonce = int(input("Nonce (how many transactions sent so far from this address): "))
    except ValueError:
        print("Enter a whole number.")
        return

    # Gas — standard ETH transfer uses 21000 gas units
    gas_limit = 21000
    gas_price_gwei = 20

    tx_data = {
        "to"      : to_address,
        "value"   : int(amount * 10 ** 18),
        "gas"     : gas_limit,
        "gasPrice": int(gas_price_gwei * 10 ** 9),
        "nonce"   : nonce,
        "chainId" : CHAIN_ID,
    }

    # Authorization gate — stops automated scripts from signing
    nickname = input("Enter authorization nickname: ").strip()
    if nickname.lower() != AUTH_NICKNAME:
        print("Wrong nickname. Cancelled.")
        return

    if not confirm_transaction(amount, to_address):
        print("Transaction rejected by user.")
        return

    # Sign
    signed = sign_transaction(private_key, tx_data)

    print("\n" + "=" * 56)
    print("  SIGNED TRANSACTION")
    print("=" * 56)
    print(f"  From    : {signed['from']}")
    print(f"  To      : {signed['to']}")
    print(f"  Amount  : {signed['value_eth']} ETH (simulated)")
    print(f"  Gas     : {signed['gas']} units @ {gas_price_gwei} Gwei")
    print(f"  Nonce   : {signed['nonce']}")
    print(f"  Chain   : {signed['chainId']} (Sepolia testnet)")
    print(f"  TX Hash : {signed['txHash'][:24]}...")
    print(f"  Raw TX  : {signed['rawTransaction'][:30]}...")
    print("=" * 56)

    save_signed_tx(signed, SIGNED_TX_OUTPUT)

    print(f"\nsigned_tx.json saved.")
    print("Transfer it to an internet-connected device when you are")
    print("ready to submit it to the network.")

    # Update local simulated balance
    update_balance(wallet_address, balance - amount)
    print(f"\nSimulated balance updated: {get_balance(wallet_address)} ETH")

    # Append to the tamper-evident log
    log_transaction(
        from_address=wallet_address,
        to_address=to_address,
        amount=amount,
        tx_hash=signed["txHash"],
        signature=signed["rawTransaction"][:64],
    )

    display_wallet_info(wallet_address, get_balance(wallet_address))


# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------

def main():
    # Load existing wallet on startup if one exists
    if os.path.exists(WALLET_FILE):
        private_key    = load_wallet()
        wallet_address = eth_address(private_key.public_key)
        print(f"\nWallet loaded: {wallet_address}")
    else:
        private_key    = None
        wallet_address = None

    while True:
        print("\n" + "=" * 40)
        print("     CryptoPasal  |  Offline Wallet")
        print("=" * 40)
        print("  1. Create Wallet")
        print("  2. Sign Transaction")
        print("  3. Show Address + QR Code")
        print("  4. Show Balance")
        print("  5. Transaction History")
        print("  6. Exit")
        print("=" * 40)

        choice = input("> ").strip()

        if choice == "1":
            wallet_address, private_key = create_wallet()

        elif choice == "2":
            if not wallet_address or not private_key:
                print("No wallet loaded. Create one first (option 1).")
            else:
                sign_tx(wallet_address, private_key)

        elif choice == "3":
            if wallet_address:
                print(f"\nAddress: {wallet_address}")
                generate_qr(wallet_address, title="SCAN TO RECEIVE")
            else:
                print("No wallet loaded.")

        elif choice == "4":
            if wallet_address:
                print(f"\n  Address      : {wallet_address}")
                print(f"  Balance      : {get_balance(wallet_address)} ETH (simulated)")
                print(f"  Transactions : {get_tx_count()}")
            else:
                print("No wallet loaded.")

        elif choice == "5":
            show_history()

        elif choice == "6":
            print("\nGoodbye.")
            break

        else:
            print("Enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
