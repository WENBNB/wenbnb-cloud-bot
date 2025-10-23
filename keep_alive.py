# ==========================================
# 💖 WENBNB Neural Engine — Keep-Alive Service
# Keeps Render Free Plan alive 24×7 using pings
# ==========================================

import threading
import time
import requests
import os

# 🌐 Render service public URL (update this!)
PING_URL = os.getenv("RENDER_APP_URL", "https://wenbnb-neural-engine.onrender.com")
INTERVAL = 600  # every 10 minutes

def keep_alive():
    while True:
        try:
            response = requests.get(PING_URL, timeout=10)
            if response.status_code == 200:
                print(f"✅ Keep-Alive: Bot is up! ({PING_URL})")
            else:
                print(f"⚠️ Keep-Alive Warning: {response.status_code}")
        except Exception as e:
            print(f"❌ Keep-Alive Error: {e}")
        time.sleep(INTERVAL)

def start_keep_alive():
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()
