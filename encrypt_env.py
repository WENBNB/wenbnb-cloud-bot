# ===============================================
# 🔒 WENBNB Neural Engine - Environment Encryptor v2.0
# AES-256-GCM secure .env encryption/decryption utility
# ===============================================

import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_env(input_file=".env", output_file=".env.encrypted", key_file=".env.key"):
    # Generate AES-256 key
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)

    # Read env data
    with open(input_file, "rb") as f:
        data = f.read()

    # Generate nonce (random 12 bytes)
    nonce = os.urandom(12)

    # Encrypt
    encrypted = aesgcm.encrypt(nonce, data, None)

    # Save encrypted file
    with open(output_file, "wb") as f:
        f.write(nonce + encrypted)

    # Save key
    with open(key_file, "wb") as f:
        f.write(base64.b64encode(key))

    print("✅ .env file encrypted successfully!")
    print(f"🔐 Encrypted: {output_file}")
    print(f"🔑 Key saved to: {key_file}")
    print("\n⚠️ Keep your .env.key file PRIVATE (Render Secret Files only).")

def decrypt_env(encrypted_file=".env.encrypted", key_file=".env.key", output_file=".env"):
    with open(key_file, "rb") as f:
        key = base64.b64decode(f.read())

    with open(encrypted_file, "rb") as f:
        data = f.read()

    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)

    decrypted = aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_file, "wb") as f:
        f.write(decrypted)

    print("✅ .env file decrypted successfully!")

if __name__ == "__main__":
    print("🔐 WENBNB Neural Engine — Secure Environment Encryptor")
    print("1️⃣ Encrypt .env file")
    print("2️⃣ Decrypt .env.encrypted file")
    choice = input("Select (1 or 2): ").strip()

    if choice == "1":
        encrypt_env()
    elif choice == "2":
        decrypt_env()
    else:
        print("❌ Invalid choice.")
