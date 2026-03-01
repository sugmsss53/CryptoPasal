import qrcode

def generate_qr(data: str, title: str = "QR CODE"):
    """
    Generate and print a QR code directly in the terminal using ASCII.
    Works perfectly over SSH — no display or monitor needed.
    Useful for showing wallet address so others can scan and send ETH.

    Uses Reed-Solomon error correction (QR standard).
    This is also a data encoding concept relevant to cryptography.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    print("\n" + "=" * 44)
    print(f"  {title}")
    print("=" * 44)
    qr.print_ascii(invert=True)
    print("=" * 44)
    print(f"  {data}")
    print("=" * 44 + "\n")
