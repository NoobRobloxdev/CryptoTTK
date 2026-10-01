# 🔐 CryptoTTK - Ultimate Crypto & Steganography Workbench

A comprehensive Python TTK desktop application for **Cryptography, Steganography, RSA Key Management, and Password Utilities**.

---

## 🌟 Features

### 🔒 Cryptography & Hashes (`crypter.py` / `uncrypter.py`)
- **AES-256 Encryption**: Encrypt texts, individual files, or whole directories (auto-compressed as ZIP into `.enc` archives).
- **Hashing**: SHA-1, SHA-256, SHA-512, SHA3-256.
- **Dictionary Brute-force**: Built-in wordlist check for fast hash cracking.

### 🔑 Asymmetric RSA & Digital Signatures
- **Key Generator**: Generate 2048-bit RSA Public and Private keys (`.pem`).
- **Digital Signatures**: Sign files using your private key and verify signatures (`.sig`) to ensure integrity.

### 🖼️ Steganography (LSB)
- **Hide Messages in Images**: Hide secret text or encrypted payloads inside PNG image pixels (LSB algorithm).
- **Extract Secret Text**: Extract hidden payloads from PNG images.

### 🎲 Password Generator & Entropy
- **Secure Generation**: Uses Python's `secrets` module for cryptographic security.
- **Entropy Meter**: Real-time password strength calculation in bits.

---

## 📦 Requirements

- **Python 3.x**
- **Tkinter / TTK** (included with standard Python)
- **Cryptography & Pillow** (for AES, RSA & Steganography):

```bash
pip install cryptography pillow
