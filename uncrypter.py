import hashlib
import base64
import os
import zipfile
import io
import wave
import urllib.parse
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from pyzbar.pyzbar import decode as qr_decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False

COMMON_WORDS: list = ["was", "password", "123456", "admin", "hello", "secret", "minecraft", "python", "slovakia", "was", "crazy", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "qwerty", "letmein", "monkey", "dragon", "baseball", "football", "iloveyou", "starwars", "sunshine", "princess", "welcome", "shadow", "master", "superman", "harley", "batman", "trustno1", "flower", "hannah", "jordan", "tigger", "michael", "jessica", "pepper", "cookie", "ginger", "samantha", "charlie", "andrew", "michelle", "jennifer", "joshua", "daniel", "ashley", "brittany", "amanda", "sarah", "steven", "robert", "joseph", "emily", "lauren", "kayla", "alexander", "nicholas", "christopher", "anthony", "william", "james", "matthew", "david", "andrew", "ryan", "john", "daniel", "joshua", "joseph", "nicholas", "anthony", "william", "alexander", "michael", "elizabeth", "samantha", "jessica", "amanda", "sarah", "ashley", "brittany", "lauren", "kayla", "morgan", "megan", "hannah", "jordan", "courtney", "kaitlyn", "madison", "olivia", "emma", "abigail", "isabella", "sophia", "ava", "mia", "charlotte", "amelia", "harper", "evelyn", "abigail", "emily", "ella", "scarlett", "grace", "chloe", "victoria", "riley", "ariana", "lillian", "natalie", "aubrey", "zoey", "penelope", "luna", "addison", "stella", "shit", "fuck", "bitch", "asshole", "dick", "pussy", "cunt", "faggot", "nigger", "slut", "whore", "bastard", "cock", "douche", "twat", "prick", "wanker", "arsehole", "bollocks", "bugger", "git", "tosser", "penis", "dildo", "a", "b", "c" , "d", "e", "f", "g", "h" , "i", "j", "k", " l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "good", "bad", "sex", "no", "yes", "nain", "nein", "self", "harm", "the", "cat", "apple", "dictionary", "english"]

def derive_key(password: str) -> bytes:
    if HAS_CRYPTO:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt_123',
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return b""

def extract_text_from_image(img_path: str) -> str:
    if not HAS_PIL: raise Exception("Install Pillow!")
    img = Image.open(img_path).convert("RGB")
    pixels = list(img.getdata())
    binary_text = ""
    for pixel in pixels:
        for color in pixel: binary_text += str(color & 1)
    end_marker = "1111111111111110"
    pos = binary_text.find(end_marker)
    if pos != -1: binary_text = binary_text[:pos]
    chars = [chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8)]
    return "".join(chars)

def extract_text_from_wav(wav_path: str) -> str:
    with wave.open(wav_path, mode='rb') as song:
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted = [str(frame_bytes[i] & 1) for i in range(len(frame_bytes))]
    binary_text = "".join(extracted)
    end_marker = "1111111111111110"
    pos = binary_text.find(end_marker)
    if pos != -1: binary_text = binary_text[:pos]
    chars = [chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8)]
    return "".join(chars)

root = tk.Tk()
root.title("Crypto TTK - Uncrypter")
root.geometry("740x700")

style = ttk.Style()
style.theme_use("clam")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

tab1 = ttk.Frame(notebook, padding=15)
notebook.add(tab1, text="Decryption & Brute-force")

input_type = tk.StringVar(value="text")
ttk.Radiobutton(tab1, text="Text / Hash", variable=input_type, value="text").pack(anchor=tk.W)
text_entry1 = tk.Text(tab1, height=4, width=40)
text_entry1.pack(fill=tk.X, pady=(0, 10))

ttk.Radiobutton(tab1, text="Encrypted File (.enc)", variable=input_type, value="file").pack(anchor=tk.W)
f_frame = ttk.Frame(tab1)
f_frame.pack(fill=tk.X, pady=(0, 10))
file_entry1 = ttk.Entry(f_frame)
file_entry1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(f_frame, text="Browse...", command=lambda: (file_entry1.delete(0, tk.END), file_entry1.insert(0, filedialog.askopenfilename()))).pack(side=tk.RIGHT)

ttk.Label(tab1, text="Mode:").pack(anchor=tk.W)
mode_box = ttk.Combobox(tab1, values=["AES-256 Decryption", "SHA-1 Brute-force", "SHA-256 Brute-force"], state="readonly")
mode_box.set("AES-256 Decryption")
mode_box.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab1, text="Password (for AES):").pack(anchor=tk.W)
pass_entry1 = ttk.Entry(tab1, show="*")
pass_entry1.pack(fill=tk.X, pady=(0, 10))

def run_tab1():
    t_type = input_type.get()
    mode = mode_box.get()
    pwd = pass_entry1.get().strip()

    if t_type == "text":
        cipher_input = text_entry1.get("1.0", tk.END).strip()
        if not cipher_input: return
        if mode == "AES-256 Decryption":
            if not pwd: return messagebox.showwarning("Error", "Enter password!")
            try:
                dec = Fernet(derive_key(pwd)).decrypt(cipher_input.encode()).decode() if HAS_CRYPTO else "".join([chr(ord(c) ^ ord(pwd[i % len(pwd)])) for i, c in enumerate(base64.b64decode(cipher_input.encode()).decode())])
                out_entry1.delete("1.0", tk.END)
                out_entry1.insert("1.0", dec)
                res_label1.config(text="✔ Decryption successful!", foreground="green")
            except Exception:
                res_label1.config(text="✖ Invalid password or corrupted data!", foreground="red")
        else:
            h_func = hashlib.sha1 if "SHA-1" in mode else hashlib.sha256
            found = next((w for w in COMMON_WORDS if h_func(w.encode()).hexdigest().lower() == cipher_input.lower()), None)
            if found:
                out_entry1.delete("1.0", tk.END)
                out_entry1.insert("1.0", found)
                res_label1.config(text=f"✔ Hash cracked: '{found}'", foreground="green")
            else:
                res_label1.config(text="✖ Word not found in dictionary!", foreground="red")
    else:
        path = file_entry1.get().strip()
        if not os.path.exists(path) or not pwd: return messagebox.showwarning("Error", "Select file and enter password!")
        try:
            with open(path, "rb") as f: enc_data = f.read()
            dec_bytes = Fernet(derive_key(pwd)).decrypt(enc_data) if HAS_CRYPTO else bytes([b ^ ord(pwd[i % len(pwd)]) for i, b in enumerate(base64.b64decode(enc_data))])
            if dec_bytes.startswith(b"PK\x03\x04"):
                out_dir = filedialog.askdirectory(title="Select output directory")
                if out_dir:
                    with zipfile.ZipFile(io.BytesIO(dec_bytes)) as zf: zf.extractall(out_dir)
                    res_label1.config(text="✔ Folder extracted successfully!", foreground="green")
            else:
                save_p = filedialog.asksaveasfilename(title="Save decrypted file")
                if save_p:
                    with open(save_p, "wb") as f: f.write(dec_bytes)
                    res_label1.config(text="✔ File decrypted successfully!", foreground="green")
        except Exception:
            res_label1.config(text="✖ Invalid password or corrupted file!", foreground="red")

ttk.Button(tab1, text="Process", command=run_tab1).pack(pady=10)
ttk.Label(tab1, text="Output:").pack(anchor=tk.W)
out_entry1 = tk.Text(tab1, height=4)
out_entry1.pack(fill=tk.BOTH, expand=True)
res_label1 = ttk.Label(tab1, text="", font=("Helvetica", 10, "bold"))
res_label1.pack(pady=5)

tab2 = ttk.Frame(notebook, padding=15)
notebook.add(tab2, text="Decoders & Reverse Ciphers")

ttk.Label(tab2, text="Encoded Input Text:").pack(anchor=tk.W)
dec_in = tk.Text(tab2, height=4)
dec_in.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab2, text="Decoder / Cipher:").pack(anchor=tk.W)
dec_mode = ttk.Combobox(tab2, values=["Base64 Decode", "Hex Decode", "Binary Decode", "URL Decode", "ROT13", "Caesar Reverse (Shift -3)"], state="readonly")
dec_mode.set("Base64 Decode")
dec_mode.pack(fill=tk.X, pady=(0, 10))

def run_decoders():
    txt = dec_in.get("1.0", tk.END).strip()
    m = dec_mode.get()
    try:
        if m == "Base64 Decode": out = base64.b64decode(txt.encode()).decode()
        elif m == "Hex Decode": out = bytes.fromhex(txt).decode()
        elif m == "Binary Decode": out = ''.join(chr(int(b, 2)) for b in txt.split())
        elif m == "URL Decode": out = urllib.parse.unquote(txt)
        elif m == "ROT13": out = txt.translate(str.maketrans("NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"))
        elif m == "Caesar Reverse (Shift -3)":
            out = "".join([chr((ord(c) - 65 - 3) % 26 + 65) if c.isupper() else chr((ord(c) - 97 - 3) % 26 + 97) if c.islower() else c for c in txt])
        dec_out.delete("1.0", tk.END)
        dec_out.insert("1.0", out)
    except Exception as e:
        messagebox.showerror("Error", f"Decoding failed: {e}")

ttk.Button(tab2, text="Decode / Process", command=run_decoders).pack(pady=10)
ttk.Label(tab2, text="Decoded Result:").pack(anchor=tk.W)
dec_out = tk.Text(tab2, height=5)
dec_out.pack(fill=tk.BOTH, expand=True)

tab3 = ttk.Frame(notebook, padding=15)
notebook.add(tab3, text="Stego & QR Extractor")

ttk.Label(tab3, text="Carrier File (PNG Image or WAV Audio):").pack(anchor=tk.W)
steg_in_entry = ttk.Entry(tab3)
steg_in_entry.pack(fill=tk.X, pady=(0, 5))
ttk.Button(tab3, text="Select Carrier File", command=lambda: (steg_in_entry.delete(0, tk.END), steg_in_entry.insert(0, filedialog.askopenfilename()))).pack(anchor=tk.W, pady=(0, 10))

def run_steg_extract():
    p = steg_in_entry.get().strip()
    if not p: return
    try:
        if p.lower().endswith(".png"):
            msg = extract_text_from_image(p)
        elif p.lower().endswith(".wav"):
            msg = extract_text_from_wav(p)
        else: return messagebox.showwarning("Error", "Unsupported file extension!")
        steg_out_entry.delete("1.0", tk.END)
        steg_out_entry.insert("1.0", msg)
        messagebox.showinfo("Success", "Message extracted successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

ttk.Button(tab3, text="Read Hidden Message from Carrier", command=run_steg_extract).pack(fill=tk.X, pady=5)

ttk.Separator(tab3, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

def scan_qr_code():
    if not HAS_PYZBAR or not HAS_PIL: return messagebox.showerror("Error", "pyzbar / Pillow libraries missing!")
    p = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
    if not p: return
    try:
        img = Image.open(p)
        decoded = qr_decode(img)
        if decoded:
            steg_out_entry.delete("1.0", tk.END)
            steg_out_entry.insert("1.0", decoded[0].data.decode("utf-8"))
            messagebox.showinfo("QR Scanned", "QR Code decoded successfully!")
        else:
            messagebox.showwarning("QR Scan", "No QR Code found in image!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

ttk.Button(tab3, text="📷 Scan QR Code Image", command=scan_qr_code).pack(fill=tk.X, pady=5)

ttk.Label(tab3, text="Extracted Secret / Scanned Data:").pack(anchor=tk.W, pady=(10, 0))
steg_out_entry = tk.Text(tab3, height=6, wrap=tk.WORD)
steg_out_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

tab4 = ttk.Frame(notebook, padding=20)
notebook.add(tab4, text="About")

ttk.Label(tab4, text="CryptoTTK - Uncrypter", font=("Helvetica", 16, "bold")).pack(anchor=tk.W, pady=(0, 5))
ttk.Label(tab4, text="Created by: LOM_Noob", font=("Helvetica", 11, "bold"), foreground="#007acc").pack(anchor=tk.W, pady=(0, 15))

about_text = (
    "Why was CryptoTTK created?\n\n"
    "This project was inspired by a deep interest in cryptography, steganography, "
    "and mysterious internet puzzles like CICADA 3301. It serves as an all-in-one "
    "lightweight toolkit to decrypt payloads, extract secrets from PNG/WAV, scan QR codes, "
    "and solve complex security challenges."
    "and is designed to be user-friendly for both beginners and advanced users."
)

msg_label = ttk.Label(tab4, text=about_text, wraplength=520, justify=tk.LEFT)
msg_label.pack(fill=tk.X, pady=(0, 20))

link_frame = ttk.LabelFrame(tab4, text=" Official Website / Tunnel ", padding=10)
link_frame.pack(fill=tk.X, pady=5)

url_str = "https://marmalade-uncloak-unvocal.ngrok-free.dev/" # Dont DDOS/DOS this link, it's a free tunnel for testing purposes only. Use responsibly. Thank you for understanding. - LOM_Noob
url_entry = ttk.Entry(link_frame)
url_entry.insert(0, url_str)
url_entry.config(state="readonly")
url_entry.pack(fill=tk.X, pady=(0, 8))
ttk.Button(link_frame, text="🌐 Open Website in Browser", command=lambda: webbrowser.open_new(url_str)).pack(anchor=tk.W)

root.mainloop()
