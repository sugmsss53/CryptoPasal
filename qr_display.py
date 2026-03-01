import qrcode


def generate_qr(data: str, title: str = "QR CODE"):
    # Print an ASCII QR code straight to the terminal.
    # Works over SSH with no display attached — useful on a headless Pi.
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    print("\n" + "=" * 46)
    print(f"  {title}")
    print("=" * 46)
    qr.print_ascii(invert=True)
    print("=" * 46)
    print(f"  {data}")
    print("=" * 46 + "\n")
