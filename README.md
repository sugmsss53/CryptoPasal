# CryptoPasal 🔐

An open-source, air-gapped Ethereum hardware wallet simulator built in Python. Sign transactions offline using ECDSA secp256k1 — your private key never touches the internet.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square)

---

## What It Does

- Generates a 24-word BIP-39 mnemonic wallet from secure random entropy
- Derives your Ethereum address using secp256k1 + Keccak-256
- Signs transactions offline with ECDSA (EIP-155 replay protection included)
- Encrypts your private key at rest with AES-128 (Fernet)
- Maintains a SHA-256 hash-chained transaction log — tamper is detected instantly
- Displays your wallet address as a terminal QR code
- Outputs `signed_tx.json` — ready to broadcast when internet access is available

---

## Installation

```bash
git clone https://github.com/sugmsss53/CryptoPasal.git
cd CryptoPasal
pip install -r requirements.txt
python main.py
```

---

## Raspberry Pi Setup

**1. Flash Raspberry Pi OS Lite** onto a MicroSD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

**2. Update the system**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3-pip -y
```

**3. Clone and install**
```bash
git clone https://github.com/sugmsss53/CryptoPasal.git
cd CryptoPasal
pip3 install -r requirements.txt --break-system-packages
```

**4. Disable Wi-Fi (air-gap)**
```bash
sudo rfkill block wifi
```
Unplug the Ethernet cable. The Pi should have no internet connection while CryptoPasal is in use.

**5. Run**
```bash
python3 main.py
```

**6. Transfer signed transactions via USB**
```bash
sudo mount /dev/sda1 /mnt/usb
cp signed_tx.json /mnt/usb/
sudo umount /mnt/usb
```
Take the USB to an internet-connected machine to broadcast the transaction when ready.

---

## Project Structure

```
CryptoPasal/
├── main.py            # Entry point and CLI menu
├── entropy.py         # CSPRNG entropy (os.urandom)
├── wallet_mnemonic.py # BIP-39 mnemonic and seed derivation
├── keygen.py          # Private/public key generation
├── address.py         # Ethereum address (Keccak-256)
├── signer.py          # ECDSA transaction signing
├── storage.py         # AES encrypted key storage
├── tx_history.py      # Hash-chained audit log
├── ui_mock.py         # OLED-simulated terminal UI
├── qr_display.py      # Terminal QR code
└── requirements.txt
```

> ⚠️ Never share or commit `wallet.enc` or `secret.key`

---

## Dependencies

```
cryptography, mnemonic, ecdsa, eth-utils, eth-keys, eth-account, web3, qrcode
```

---

## Roadmap

- [ ] Live transaction broadcasting via sandboxed internet-access pathway
- [ ] BIP-44 HD key derivation
- [ ] PKCS#12 keystore format
- [ ] Hardware PIN entry (physical keypad)
- [ ] pytest test suite + CI/CD

---

## License

MIT — free to use, modify, and distribute with attribution.
