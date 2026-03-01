W = 34  


def _box_line(content=""):
    return "|" + content.ljust(W) + "|"


def confirm_transaction(amount, to_address):
    # Mimics the confirmation screen on a physical hardware wallet.
    # The user must explicitly press Y before anything gets signed.
    print("\n+" + "-" * W + "+")
    print(_box_line(" CONFIRM TRANSACTION"))
    print(_box_line())
    print(_box_line(" To:"))
    print(_box_line("  " + to_address[:W - 2]))
    print(_box_line("  " + to_address[W - 2:]))
    print(_box_line())
    print(_box_line(f" Amount : {amount} ETH (simulated)"))
    print(_box_line())
    print("|" + "  Y = Confirm    N = Reject  ".center(W) + "|")
    print("+" + "-" * W + "+\n")

    while True:
        choice = input("Confirm? (Y/N): ").strip().lower()
        if choice == "y":
            return True
        if choice == "n":
            return False
        print("Enter Y or N.")


def display_message(message):
    print("\n+" + "-" * W + "+")
    print(_box_line(" " + message))
    print("+" + "-" * W + "+\n")


def display_wallet_info(address, balance):
    print("\n+" + "-" * W + "+")
    print(_box_line(" WALLET"))
    print(_box_line())
    print(_box_line(" " + address[:W - 1]))
    print(_box_line(" " + address[W - 1:]))
    print(_box_line())
    print(_box_line(f" Balance : {balance} ETH (simulated)"))
    print("+" + "-" * W + "+\n")
