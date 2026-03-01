def confirm_transaction(amount, to_address):
    """
    Simulates an OLED screen confirmation dialog in the terminal.
    On a real hardware wallet this would be a physical screen + buttons.
    Returns True if user confirms, False if rejected.
    """
    oled_width = 32
    print("\n+" + "-" * oled_width + "+")
    print("|" + " CONFIRM TRANSACTION ".center(oled_width) + "|")
    print("|" + " " * oled_width + "|")
    print("|" + f"TO:".ljust(oled_width) + "|")
    print("|" + f"  {to_address[:28]}".ljust(oled_width) + "|")
    print("|" + f"  {to_address[28:]}".ljust(oled_width) + "|")
    print("|" + " " * oled_width + "|")
    print("|" + f"AMOUNT: {amount} ETH".ljust(oled_width) + "|")
    print("|" + " " * oled_width + "|")
    print("|" + "Y = Confirm    N = Reject".center(oled_width) + "|")
    print("+" + "-" * oled_width + "+\n")

    while True:
        choice = input("Press Y to confirm, N to reject: ").strip().lower()
        if choice == "y":
            return True
        elif choice == "n":
            return False
        else:
            print("Invalid input. Press Y or N only.")

def display_message(message):
    """Display a single message in OLED style box."""
    oled_width = 32
    print("\n+" + "-" * oled_width + "+")
    print("|" + message.center(oled_width) + "|")
    print("+" + "-" * oled_width + "+\n")

def display_wallet_info(address, balance):
    """
    Display wallet address and balance in OLED style.
    Address is split across two lines to fit the display width.
    """
    oled_width = 32
    print("\n+" + "-" * oled_width + "+")
    print("|" + " WALLET INFO ".center(oled_width) + "|")
    print("|" + " " * oled_width + "|")
    print("|" + "Address:".ljust(oled_width) + "|")
    print("|" + f"  {address[:20]}".ljust(oled_width) + "|")
    print("|" + f"  {address[20:]}".ljust(oled_width) + "|")
    print("|" + " " * oled_width + "|")
    print("|" + f"Balance: {balance} ETH".ljust(oled_width) + "|")
    print("+" + "-" * oled_width + "+\n")
