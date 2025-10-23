# =========================
# 🧠 WENBNB Neural Engine v5.0
# Dual Engine Launch (AI + Dashboard)
# =========================

# Main AI Telegram Bot
worker: python3 wenbot.py

# Flask Web Dashboard
web: gunicorn dashboard.dashboard:app --workers 2 --threads 2 --timeout 120
