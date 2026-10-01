import hashlib
import base64
import os
import math
import secrets
import string
import zipfile
import io
import urllib.parse
import wave
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Optional dependencies
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
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
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

MODES = ["AES-256 (Password)", "SHA-1 Hash", "SHA-256 Hash", "SHA-512 Hash", "SHA3-256 Hash"]

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

def calculate_entropy(password: str) -> float:
    if not password: return 0.0
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(c in string.punctuation for c in password): charset += 32
    if charset == 0: charset = 256
    return len(password) * math.log2(charset)

# --- Steganography Functions ---
def hide_text_in_image(img_path: str, secret_text: str, out_path: str):
    if not HAS_PIL: raise Exception("Pillow library missing!")
    img = Image.open(img_path).convert("RGB")
    binary_text = "".join(format(ord(c), "08b") for c in secret_text) + "1111111111111110"
    pixels = list(img.getdata())
    if len(binary_text) > len(pixels) * 3:
        raise Exception("Image is too small for message!")
    new_pixels = []
    idx = 0
    for r, g, b in pixels:
        if idx < len(binary_text): r = (r & ~1) | int(binary_text[idx]); idx += 1
        if idx < len(binary_text): g = (g & ~1) | int(binary_text[idx]); idx += 1
        if idx < len(binary_text): b = (b & ~1) | int(binary_text[idx]); idx += 1
        new_pixels.append((r, g, b))
    img.putdata(new_pixels)
    img.save(out_path, "PNG")

def hide_text_in_wav(wav_in: str, secret_text: str, wav_out: str):
    with wave.open(wav_in, mode='rb') as song:
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    binary_text = "".join(format(ord(c), "08b") for c in secret_text) + "1111111111111110"
    if len(binary_text) > len(frame_bytes):
        raise Exception("Audio file too small!")
    for i in range(len(binary_text)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_text[i])
    with wave.open(wav_out, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_bytes)

# --- Shredder Function ---
def secure_shred_file(filepath: str, passes: int = 3):
    if not os.path.isfile(filepath): raise Exception("File not found!")
    length = os.path.getsize(filepath)
    with open(filepath, "ba+", buffering=0) as f:
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(length))
    os.remove(filepath)

# --- GUI ---
root = tk.Tk()
root.title("Crypto TTK - Crypter Ultimate Suite")
root.geometry("740x700")

style = ttk.Style()
style.theme_use("clam")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# TAB 1: Text & Files
tab1 = ttk.Frame(notebook, padding=15)
notebook.add(tab1, text="Text & Files")

input_type = tk.StringVar(value="text")
ttk.Radiobutton(tab1, text="Text", variable=input_type, value="text").pack(anchor=tk.W)
text_entry1 = tk.Text(tab1, height=4, width=40)
text_entry1.pack(fill=tk.X, pady=(0, 10))

ttk.Radiobutton(tab1, text="File / Folder", variable=input_type, value="file").pack(anchor=tk.W)
f_frame = ttk.Frame(tab1)
f_frame.pack(fill=tk.X, pady=(0, 10))
file_entry1 = ttk.Entry(f_frame)
file_entry1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(f_frame, text="File", command=lambda: (file_entry1.delete(0, tk.END), file_entry1.insert(0, filedialog.askopenfilename()))).pack(side=tk.LEFT, padx=2)
ttk.Button(f_frame, text="Folder", command=lambda: (file_entry1.delete(0, tk.END), file_entry1.insert(0, filedialog.askdirectory()))).pack(side=tk.LEFT)

ttk.Label(tab1, text="Mode:").pack(anchor=tk.W)
mode_box = ttk.Combobox(tab1, values=MODES, state="readonly")
mode_box.set("AES-256 (Password)")
mode_box.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab1, text="Password (for AES):").pack(anchor=tk.W)
pass_entry1 = ttk.Entry(tab1, show="*")
pass_entry1.pack(fill=tk.X, pady=(0, 10))

def run_tab1():
    t_type = input_type.get()
    mode = mode_box.get()
    pwd = pass_entry1.get().strip()
    
    if t_type == "text":
        txt = text_entry1.get("1.0", tk.END).strip()
        if not txt: return
        if mode == "AES-256 (Password)":
            if not pwd: return messagebox.showwarning("Error", "Enter password!")
            out = Fernet(derive_key(pwd)).encrypt(txt.encode()).decode() if HAS_CRYPTO else base64.b64encode("".join([chr(ord(c) ^ ord(pwd[i % len(pwd)])) for i, c in enumerate(txt)]).encode()).decode()
        elif "SHA-1" in mode: out = hashlib.sha1(txt.encode()).hexdigest()
        elif "SHA-256" in mode: out = hashlib.sha256(txt.encode()).hexdigest()
        elif "SHA-512" in mode: out = hashlib.sha512(txt.encode()).hexdigest()
        elif "SHA3-256" in mode: out = hashlib.sha3_256(txt.encode()).hexdigest()
        out_entry1.delete("1.0", tk.END)
        out_entry1.insert("1.0", out)
    else:
        path = file_entry1.get().strip()
        if not os.path.exists(path): return messagebox.showwarning("Error", "Path does not exist!")
        if os.path.isdir(path):
            mem_zip = io.BytesIO()
            with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for r_dir, _, files in os.walk(path):
                    for file in files:
                        fp = os.path.join(r_dir, file)
                        zf.write(fp, os.path.relpath(fp, path))
            data_bytes = mem_zip.getvalue()
        else:
            with open(path, "rb") as f: data_bytes = f.read()

        if mode == "AES-256 (Password)":
            if not pwd: return messagebox.showwarning("Error", "Enter password!")
            save_p = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted", "*.enc")])
            if not save_p: return
            enc_data = Fernet(derive_key(pwd)).encrypt(data_bytes) if HAS_CRYPTO else base64.b64encode(bytes([b ^ ord(pwd[i % len(pwd)]) for i, b in enumerate(data_bytes)]))
            with open(save_p, "wb") as f_out: f_out.write(enc_data)
            messagebox.showinfo("Success", f"Saved to: {save_p}")
        else:
            h = hashlib.sha256(data_bytes).hexdigest()
            out_entry1.delete("1.0", tk.END)
            out_entry1.insert("1.0", h)

ttk.Button(tab1, text="Process", command=run_tab1).pack(pady=10)
ttk.Label(tab1, text="Output / Hash:").pack(anchor=tk.W)
out_entry1 = tk.Text(tab1, height=4)
out_entry1.pack(fill=tk.BOTH, expand=True)

# TAB 2: Encoders & Ciphers
tab2 = ttk.Frame(notebook, padding=15)
notebook.add(tab2, text="Encoders & Ciphers")

ttk.Label(tab2, text="Input Text:").pack(anchor=tk.W)
enc_in = tk.Text(tab2, height=4)
enc_in.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab2, text="Format / Cipher:").pack(anchor=tk.W)
enc_mode = ttk.Combobox(tab2, values=["Base64 Encode", "Base64 Decode", "Hex Encode", "Hex Decode", "Binary Encode", "Binary Decode", "URL Encode", "URL Decode", "ROT13", "Caesar (Shift 3)"], state="readonly")
enc_mode.set("Base64 Encode")
enc_mode.pack(fill=tk.X, pady=(0, 10))

def run_encoders():
    txt = enc_in.get("1.0", tk.END).strip()
    m = enc_mode.get()
    try:
        if m == "Base64 Encode": out = base64.b64encode(txt.encode()).decode()
        elif m == "Base64 Decode": out = base64.b64decode(txt.encode()).decode()
        elif m == "Hex Encode": out = txt.encode().hex()
        elif m == "Hex Decode": out = bytes.fromhex(txt).decode()
        elif m == "Binary Encode": out = ' '.join(format(ord(c), '08b') for c in txt)
        elif m == "Binary Decode": out = ''.join(chr(int(b, 2)) for b in txt.split())
        elif m == "URL Encode": out = urllib.parse.quote(txt)
        elif m == "URL Decode": out = urllib.parse.unquote(txt)
        elif m == "ROT13": out = txt.translate(str.maketrans("NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"))
        elif m == "Caesar (Shift 3)":
            out = "".join([chr((ord(c) - 65 + 3) % 26 + 65) if c.isupper() else chr((ord(c) - 97 + 3) % 26 + 97) if c.islower() else c for c in txt])
        enc_out.delete("1.0", tk.END)
        enc_out.insert("1.0", out)
    except Exception as e:
        messagebox.showerror("Error", f"Transformation failed: {e}")

ttk.Button(tab2, text="Convert / Process", command=run_encoders).pack(pady=10)
ttk.Label(tab2, text="Result:").pack(anchor=tk.W)
enc_out = tk.Text(tab2, height=5)
enc_out.pack(fill=tk.BOTH, expand=True)

# TAB 3: File Hashes & Integrity
tab3 = ttk.Frame(notebook, padding=15)
notebook.add(tab3, text="File Hashes & Integrity")

ttk.Label(tab3, text="Select File for Hash Check:").pack(anchor=tk.W)
hash_file_entry = ttk.Entry(tab3)
hash_file_entry.pack(fill=tk.X, pady=(0, 5))

def calc_file_hashes():
    p = hash_file_entry.get().strip()
    if not os.path.isfile(p): return messagebox.showwarning("Error", "File does not exist!")
    with open(p, "rb") as f: data = f.read()
    
    md5_val = hashlib.md5(data).hexdigest()
    sha1_val = hashlib.sha1(data).hexdigest()
    sha256_val = hashlib.sha256(data).hexdigest()
    
    hash_res_txt.delete("1.0", tk.END)
    hash_res_txt.insert(tk.END, f"MD5:    {md5_val}\nSHA1:   {sha1_val}\nSHA256: {sha256_val}")

ttk.Button(tab3, text="Browse & Compute Hashes", command=lambda: (hash_file_entry.delete(0, tk.END), hash_file_entry.insert(0, filedialog.askopenfilename()), calc_file_hashes())).pack(anchor=tk.W, pady=(0, 10))

hash_res_txt = tk.Text(tab3, height=4)
hash_res_txt.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab3, text="Verify Expected Hash:").pack(anchor=tk.W)
exp_hash_entry = ttk.Entry(tab3)
exp_hash_entry.pack(fill=tk.X, pady=(0, 5))

def verify_hash_match():
    exp = exp_hash_entry.get().strip().lower()
    curr = hash_res_txt.get("1.0", tk.END).lower()
    if exp in curr and len(exp) > 8:
        match_label.config(text="✔ HASH MATCHED! File integrity verified.", foreground="green")
    else:
        match_label.config(text="✖ HASH MISMATCH! File modified or wrong hash.", foreground="red")

ttk.Button(tab3, text="Check Match", command=verify_hash_match).pack(anchor=tk.W, pady=(0, 5))
match_label = ttk.Label(tab3, text="", font=("Helvetica", 10, "bold"))
match_label.pack(anchor=tk.W)

# TAB 4: Steganography (PNG & WAV)
tab4 = ttk.Frame(notebook, padding=15)
notebook.add(tab4, text="Steganography & QR")

steg_type = tk.StringVar(value="png")
ttk.Radiobutton(tab4, text="PNG Image", variable=steg_type, value="png").pack(anchor=tk.W)
ttk.Radiobutton(tab4, text="WAV Audio", variable=steg_type, value="wav").pack(anchor=tk.W)

ttk.Label(tab4, text="Secret Message:").pack(anchor=tk.W, pady=(5, 0))
steg_msg_entry = tk.Text(tab4, height=3)
steg_msg_entry.pack(fill=tk.X, pady=(0, 10))

ttk.Label(tab4, text="Carrier File:").pack(anchor=tk.W)
steg_carrier_entry = ttk.Entry(tab4)
steg_carrier_entry.pack(fill=tk.X, pady=(0, 5))
ttk.Button(tab4, text="Select Carrier File", command=lambda: (steg_carrier_entry.delete(0, tk.END), steg_carrier_entry.insert(0, filedialog.askopenfilename()))).pack(anchor=tk.W, pady=(0, 10))

def run_steg_hide():
    st = steg_type.get()
    msg = steg_msg_entry.get("1.0", tk.END).strip()
    car = steg_carrier_entry.get().strip()
    if not msg or not car: return messagebox.showwarning("Error", "Missing input!")
    
    if st == "png":
        out_p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if out_p: hide_text_in_image(car, msg, out_p); messagebox.showinfo("Success", "Saved PNG!")
    else:
        out_p = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if out_p: hide_text_in_wav(car, msg, out_p); messagebox.showinfo("Success", "Saved WAV!")

ttk.Button(tab4, text="Hide Message in Carrier", command=run_steg_hide).pack(fill=tk.X, pady=(0, 15))

# QR Code Generator
ttk.Separator(tab4, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
ttk.Label(tab4, text="QR Code Generator:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)

def gen_qr():
    if not HAS_QR: return messagebox.showerror("Error", "qrcode library not installed!")
    txt = steg_msg_entry.get("1.0", tk.END).strip()
    if not txt: return messagebox.showwarning("Error", "Enter message in Secret Message box!")
    out_p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
    if out_p:
        img = qrcode.make(txt)
        img.save(out_p)
        messagebox.showinfo("Success", "QR Code Generated!")

ttk.Button(tab4, text="Generate QR Code from Message", command=gen_qr).pack(fill=tk.X, pady=5)

# TAB 5: Shredder & Security Utilities
tab5 = ttk.Frame(notebook, padding=15)
notebook.add(tab5, text="Shredder & Passwords")

ttk.Label(tab5, text="Secure File Shredder (DoD Overwrite):", font=("Helvetica", 11, "bold"), foreground="red").pack(anchor=tk.W)
shred_file_entry = ttk.Entry(tab5)
shred_file_entry.pack(fill=tk.X, pady=5)

def run_shred():
    fp = shred_file_entry.get().strip()
    if not os.path.isfile(fp): return messagebox.showwarning("Error", "File not found!")
    if messagebox.askyesno("CONFIRM DESTRUCTION", f"Are you sure you want to PERMANENTLY SHRED:\n{fp}\nThis CANNOT be undone!"):
        try:
            secure_shred_file(fp)
            messagebox.showinfo("Shredded", "File successfully destroyed!")
            shred_file_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

ttk.Button(tab5, text="Select File & Shred Permanently", command=lambda: (shred_file_entry.delete(0, tk.END), shred_file_entry.insert(0, filedialog.askopenfilename()))).pack(anchor=tk.W, pady=2)
ttk.Button(tab5, text="🔥 SHRED FILE NOW", command=run_shred).pack(fill=tk.X, pady=(5, 20))

ttk.Separator(tab5, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
ttk.Label(tab5, text="Password Generator:").pack(anchor=tk.W)

def generate_pwd():
    length = int(len_spin.get())
    chars = string.ascii_letters + string.digits + string.punctuation
    pwd = "".join(secrets.choice(chars) for _ in range(length))
    gen_pass_entry.delete(0, tk.END)
    gen_pass_entry.insert(0, pwd)
    ent = calculate_entropy(pwd)
    entropy_label.config(text=f"Entropy: {ent:.1f} bits", foreground="green" if ent >= 70 else "orange" if ent >= 40 else "red")

len_spin = ttk.Spinbox(tab5, from_=6, to=64, value=16)
len_spin.pack(fill=tk.X, pady=5)
ttk.Button(tab5, text="Generate Secure Password", command=generate_pwd).pack(fill=tk.X, pady=5)
gen_pass_entry = ttk.Entry(tab5)
gen_pass_entry.pack(fill=tk.X, pady=5)
entropy_label = ttk.Label(tab5, text="Entropy: 0 bits", font=("Helvetica", 10, "bold"))
entropy_label.pack(pady=5)

# TAB 6: About
tab6 = ttk.Frame(notebook, padding=20)
notebook.add(tab6, text="About")

ttk.Label(tab6, text="CryptoTTK Ultimate Suite", font=("Helvetica", 16, "bold")).pack(anchor=tk.W, pady=(0, 5))
ttk.Label(tab6, text="Created by: LOM_Noob", font=("Helvetica", 11, "bold"), foreground="#007acc").pack(anchor=tk.W, pady=(0, 15))

about_text = (
    "Why was CryptoTTK created?\n\n"
    "This project was inspired by a deep interest in cryptography, steganography, "
    "and mysterious internet puzzles like CICADA 3301. It serves as an all-in-one "
    "lightweight toolkit to encrypt payloads, hide secrets inside images & WAV audio, "
    "generate keys, shred data, and solve complex security challenges."
)

msg_label = ttk.Label(tab6, text=about_text, wraplength=520, justify=tk.LEFT)
msg_label.pack(fill=tk.X, pady=(0, 20))

link_frame = ttk.LabelFrame(tab6, text=" Official Website / Tunnel ", padding=10)
link_frame.pack(fill=tk.X, pady=5)

url_str = "https://marmalade-uncloak-unvocal.ngrok-free.dev/"
url_entry = ttk.Entry(link_frame)
url_entry.insert(0, url_str)
url_entry.config(state="readonly")
url_entry.pack(fill=tk.X, pady=(0, 8))
ttk.Button(link_frame, text="🌐 Open Website in Browser", command=lambda: webbrowser.open_new(url_str)).pack(anchor=tk.W)

root.mainloop()