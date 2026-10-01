# 🔐 CryptoTTK Ultimate Suite

**CryptoTTK** je komplexný Swiss Army Knife nástroj v Pythone (s GUI postaveným na Tkinter/TTK) určený na kryptografiu, steganografiu, skartáciu dát a prácu s rôznymi typmi kódovania. Projekt bol inšpirovaný internetovými záhadami (ako Cicada 3301) a slúži ako univerzálny pomocník pre CTF výzvy, bezpečnosť a prácu so šifrovanými dátami.

---

## 🚀 Hlavné Funkcie (Features)

### 🔏 1. Šifrovanie & Dešifrovanie (Text & Súbory)
* **AES-256 (PBKDF2 HMAC SHA-256)** šifrovanie a dešifrovanie textu aj celých súborov/zložiek.
* Krypto-fallbacky v prípade absencie externých knižníc.
* Hashovanie textu cez **SHA-1, SHA-256, SHA-512, SHA3-256**.
* Integrovaný slovníkový **Brute-force cracker** pre základné SHA-1/SHA-256 hashe.

### 🔠 2. Enkodéry & Šifry (Base & Ciphers)
* Konverzia textu medzi rôznymi formátmi:
  * **Base64** Encode / Decode
  * **Hexadecimal** (Hex) Encode / Decode
  * **Binary** (010101) Encode / Decode
  * **URL** Encoding / Decoding
  * **ROT13** Cipher
  * **Caesar Cipher** (Shift +3 / Shift -3)

### 🔍 3. Kontrola Integrity & Hashe Súborov
* Výpočet **MD5, SHA-1 a SHA-256** hashov pre akýkoľvek súbor naraz.
* **Porovnávač hashov (Integrity Checker):** Vizuálne overenie, či sa vypočítaný hash zhoduje s očakávaným (zelené/červené zvýraznenie).

### 🖼️ 🔊 4. Steganografia (PNG & WAV)
* **PNG Steganografia:** Ukrytie a čítanie tajných textových správ priamo v pixeloch obrázka (LSB metóda).
* **WAV Audio Steganografia:** Ukrytie a čítanie správ v audio súboroch vo formáte WAV.

### 📱 5. QR Code Generátor & Skener
* Generovanie QR kódov z vybraného textu alebo šifrovaného tokenu do PNG súboru.
* Skenovanie a dekódovanie QR kódov z obrázkov pomocou knižnice `pyzbar`.

### 🔥 6. Bezpečný Skartovač Súborov (File Shredder)
* Nenávratné vymazanie citlivých súborov prepísaním náhodnými bajtmi (vstavaný DoD štandard overwrite) pred samotným odstránením z disku.

### 🔑 7. Generátor Hesiel & Entropia
* Generátor kryptograficky bezpečných random hesiel s voľbou dĺžky.
* Výpočet a vizuálne zobrazenie **entropie hesla v bitoch**.

---

## 📦 Inštalácia Požadovaných Knižníc

Pre plnú funkčnosť všetkých modulov (QR, Stego, AES) nainštaluj potrebné závislosti:

```powershell
pip install cryptography pillow qrcode pyzbar
