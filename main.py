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

# ============================================================
# CONFIGURATION
# ============================================================

WALLET_FILE   = "wallet.enc"
BALANCES_FILE = "balances.json"

# Signed transaction output path
# VS Code / laptop testing  → "signed_tx.json"
# Pi with pendrive          → "/mnt/usb/signed_tx.json"
SIGNED_TX_OUTPUT = "signed_tx.json"

# Ethereum network
# 11155111 = Sepolia testnet (use this for testing — free fake ETH)
# 1        = Ethereum mainnet (real money — use only when ready)
CHAIN_ID = 11155111

# ============================================================


def get_mock_balance(address):
    """Return simulated ETH balance from local file."""
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, "r") as f:
            balances = json.load(f)
    else:
        balances = {}
    return balances.get(address, 5.0)


def update_mock_balance(address, new_balance):
    """Update simulated ETH balance in local file."""
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, "r") as f:
            balances = json.load(f)
    else:
        balances = {}
    balances[address] = new_balance
    with open(BALANCES_FILE, "w") as f:
        json.dump(balances, f)


def create_wallet():
    """
    Full wallet creation flow:
    entropy → mnemonic → seed → private key → address → encrypted storage
    """
    mnemonic = generate_mnemonic()

    # Display seed phrase clearly numbered
    print("\n" + "=" * 52)
    print("   WRITE DOWN YOUR SEED PHRASE (24 words)")
    print("=" * 52)
    words = mnemonic.split()
    for i, word in enumerate(words, 1):
        print(f"   {i:2}. {word}")
    print("=" * 52)
    print("   Store this safely — NEVER save it digitally.")
    print("   This is shown ONCE and never again.")
    print("=" * 52 + "\n")

    # Derive keys
    seed        = mnemonic_to_seed(mnemonic)
    private_key = generate_private_key(seed)
    public_key  = private_key.public_key
    wallet_addr = eth_address(public_key)

    # Encrypt and store private key
    store_wallet(private_key)

    print("Wallet created and securely stored (AES encrypted).")
    print(f"\nYOUR WALLET ADDRESS:\n{wallet_addr}")
    print(f"\nSimulated balance: {get_mock_balance(wallet_addr)} ETH")

    # Show address as QR code
    generate_qr(wallet_addr, title="YOUR WALLET ADDRESS — SCAN TO RECEIVE ETH")

    return wallet_addr, private_key


def sign_tx(wallet_address, private_key):
    """
    Build and sign a real Ethereum transaction.
    Saves signed_tx.json which broadcast_tx.py uses to send to network.
    """
    print("\n--- NEW TRANSACTION ---")

    # Recipient address
    to_address = input("To Address: ").strip()

    # Validate address format
    if not to_address.startswith("0x"):
        print(f"Invalid address: must start with 0x. You entered: {to_address[:10]}...")
        return
    if len(to_address) != 42:
        print(f"Invalid address length: got {len(to_address)} characters, need exactly 42.")
        print(f"  Your input : {to_address}")
        print(f"  Example    : 0x71C7656EC7ab88b098defB751B7401B5f6d8976F")
        return
    try:
        int(to_address[2:], 16)
    except ValueError:
        print("Invalid address: contains non-hex characters.")
        return

    # Convert to EIP-55 checksum format — required by eth_account
    from web3 import Web3
    to_address = Web3.to_checksum_address(to_address)

    # Amount
    try:
        amount_eth = float(input("Amount (ETH): "))
    except ValueError:
        print("Invalid amount.")
        return

    if amount_eth <= 0:
        print("Amount must be greater than 0.")
        return

    # Check simulated balance
    balance = get_mock_balance(wallet_address)
    if amount_eth > balance:
        print(f"Insufficient balance. You have {balance} ETH.")
        return

    # Nonce — number of transactions sent from this address
    try:
        nonce = int(input("Nonce (0 if this is your first transaction): "))
    except ValueError:
        print("Invalid nonce.")
        return

    # Gas price fixed at 160 Nepal
    gas_nepal = 160

    # Build real Ethereum transaction
    tx_data = {
        "to"      : to_address,
        "value"   : int(amount_eth * 10**18),    # ETH → Wei
        "gas"     : 21000,                        # standard transfer gas limit
        "gasPrice": int(gas_nepal * 10**9),       # Nepal → Wei
        "nonce"   : nonce,
        "chainId" : CHAIN_ID,
    }

    # Nickname verification before signing
    nickname = input("Enter your nickname to authorize transaction: ").strip()
    if nickname.lower() != "bojack":
        print("Wrong nickname. Transaction cancelled.")
        return

    # Confirm via OLED-style screen
    if confirm_transaction(amount_eth, to_address):

        # Sign with ECDSA secp256k1
        signed = sign_transaction(private_key, tx_data)

        # Display signed transaction details
        print("\n" + "=" * 56)
        print("  SIGNED TRANSACTION")
        print("=" * 56)
        print(f"  From              : {signed['from']}")
        print(f"  To                : {signed['to']}")
        print(f"  Amount            : {signed['value_eth']} ETH")
        print(f"  Gas Limit         : {signed['gas']}")
        print(f"  Gas Price (Nepal) : {gas_nepal}")
        print(f"  Nonce             : {signed['nonce']}")
        print(f"  Chain ID          : {signed['chainId']}")
        print(f"  TX Hash           : {signed['txHash'][:24]}...")
        print(f"  Raw TX            : {signed['rawTransaction'][:30]}...")
        print("=" * 56)

        # Save signed transaction to file
        save_signed_tx(signed, SIGNED_TX_OUTPUT)

        print(f"\nNext step:")
        print(f"  1. Copy {SIGNED_TX_OUTPUT} to your laptop")
        print(f"  2. Run: python broadcast_tx.py")
        print(f"  3. Transaction will be sent to Ethereum network")

        # Update simulated balance
        update_mock_balance(wallet_address, balance - amount_eth)
        print(f"\nSimulated balance updated: {get_mock_balance(wallet_address)} ETH")

        # Log to tamper-evident history chain
        log_transaction(
            from_address = wallet_address,
            to_address   = to_address,
            amount       = amount_eth,
            tx_hash      = signed["txHash"],
            signature    = signed["rawTransaction"][:64]
        )

    else:
        print("Transaction rejected.")

    display_wallet_info(wallet_address, get_mock_balance(wallet_address))


def show_address_qr(wallet_address):
    """Display wallet address and QR code for receiving ETH."""
    print(f"\nYOUR WALLET ADDRESS:\n{wallet_address}")
    generate_qr(wallet_address, title="SCAN TO SEND ETH TO THIS WALLET")


def main():
    # Auto-load wallet if already created
    if os.path.exists(WALLET_FILE):
        private_key    = load_wallet()
        public_key     = private_key.public_key
        wallet_address = eth_address(public_key)
        print(f"\nWallet loaded: {wallet_address}")
    else:
        private_key    = None
        wallet_address = None

    while True:
        print("\n" + "=" * 42)
        print("     CryptoPasal Hardware Wallet")
        print("=" * 42)
        print("  1. Create Wallet")
        print("  2. Sign Transaction")
        print("  3. Show Wallet Address + QR Code")
        print("  4. Show Balance")
        print("  5. Transaction History")
        print("  6. Exit")
        print("=" * 42)
        choice = input("> ").strip()

        if choice == "1":
            wallet_address, private_key = create_wallet()

        elif choice == "2":
            if not wallet_address or not private_key:
                print("No wallet found. Please create a wallet first (option 1).")
            else:
                sign_tx(wallet_address, private_key)

        elif choice == "3":
            if wallet_address:
                show_address_qr(wallet_address)
            else:
                print("No wallet found. Please create a wallet first (option 1).")

        elif choice == "4":
            if wallet_address:
                print(f"\n  Address        : {wallet_address}")
                print(f"  Balance        : {get_mock_balance(wallet_address)} ETH")
                print(f"  Transactions   : {get_tx_count()}")
            else:
                print("No wallet found. Please create a wallet first (option 1).")

        elif choice == "5":
            show_history()

        elif choice == "6":
            print("\nExiting CryptoPasal Wallet. Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()