# ============================================
# 🧠 WENBNB Neural Engine – Dockerfile v2.5 (Render Ready)
# Secure AI Telegram Bot with Auto Decrypt Environment
# ============================================

# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files into container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# 🔐 WENBNB Neural Engine – Render Auto-Decrypt Integration v2.5
# Automatically decrypts your .env.encrypted file using .env.key
# ============================================

RUN python - <<'EOF'
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key_file = ".env.key"
encrypted_file = ".env.encrypted"
output_file = ".env"

print("🔍 Checking for encrypted environment files...")
if os.path.exists(key_file) and os.path.exists(encrypted_file):
    print("🔓 Securely decrypting environment for runtime...")
    with open(key_file, "rb") as f:
        key = base64.b64decode(f.read())

    with open(encrypted_file, "rb") as f:
        data = f.read()

    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_file, "wb") as f:
        f.write(decrypted)

    print("✅ Environment successfully decrypted (WENBNB Neural Engine Active).")
else:
    print("⚠️ No encrypted environment or key found — skipping decryption.")
EOF

# ============================================
# Expose the Render port
EXPOSE 10000

# ============================================
# Start the Neural Engine (Telegram AI Bot)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:10000", "dashboard.dashboard:app"]

