# 🔐 CryptoTTK Ultimate Suite

**CryptoTTK** is a comprehensive Swiss Army Knife tool written in Python with a Tkinter/TTK GUI, designed for cryptography, steganography, secure data shredding, and encoding conversions. Inspired by internet security puzzles (such as Cicada 3301), it serves as an all-in-one suite for CTF challenges, data security, and handling encrypted payloads.

---

## 🚀 Key Features

### 🔏 1. Encryption & Decryption (Text & Files)
* **AES-256 (PBKDF2 HMAC SHA-256)** encryption and decryption for text, files, and entire directory structures.
* Built-in cryptographic fallbacks in case external libraries are absent.
* Hashing capabilities using **SHA-1, SHA-256, SHA-512, and SHA3-256**.
* Integrated dictionary **Brute-force cracker** for basic SHA-1 and SHA-256 hashes.

### 🔠 2. Encoders & Ciphers
* Multi-format data conversions:
  * **Base64** Encode / Decode
  * **Hexadecimal** (Hex) Encode / Decode
  * **Binary** (010101) Encode / Decode
  * **URL** Encoding / Decoding
  * **ROT13** Cipher
  * **Caesar Cipher** (Shift +3 / Shift -3)

### 🔍 3. File Hashes & Integrity Checker
* Simultaneous checksum calculation for **MD5, SHA-1, and SHA-256**.
* **Integrity Checker:** Visual hash matching with green/red verification alerts.

### 🖼️ 🔊 4. Steganography (PNG & WAV)
* **PNG Steganography:** Hide and extract secret text messages within image pixels using LSB (Least Significant Bit) techniques.
* **WAV Audio Steganography:** Embed and recover hidden payloads inside WAV audio files.

### 📱 5. QR Code Generator & Scanner
* Generate PNG QR codes from custom text or encrypted payloads.
* Scan and decode QR codes directly from image files using `pyzbar`.

### 🔥 6. Secure File Shredder
* Permanently destroy sensitive files using multi-pass random data overwriting (DoD standard style) before unlinking from storage.

### 🔑 7. Password Generator & Entropy Meter
* Cryptographically secure random password generator with customizable length.
* Real-time calculation and display of **password entropy in bits**.

---

## 📦 Requirements & Installation

To unlock all features (QR handling, steganography, and robust AES), install the dependencies via pip:

```powershell
pip install cryptography pillow qrcode pyzbar
