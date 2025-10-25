"""
WENBNB Reboot Monitor v8.6-R — Render-Optimized Add-On
──────────────────────────────────────────────────────────────
Purpose:
- Detects Render container or system restarts
- Alerts admin(s) instantly when Neural Engine reboots
- Logs uptime since last reboot
- Works alongside maintenance_core.py & system_monitor.py

💫 Powered by WENBNB Neural Engine — Uptime Awareness Layer 24×7
"""

import os, time, json, platform
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [5698007588]  # your Telegram ID 💋
LOG_FILE = "data/reboot_status.json"
BRAND_TAG = "💫 WENBNB Neural Engine — Uptime Awareness Layer 24×7"

# === Ensure data dir exists ===
os.makedirs("data", exist_ok=True)


# === Load/Save Reboot Info ===
def load_last_status():
    if not os.path.exists(LOG_FILE):
        return {}
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_last_status(data):
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[RebootMonitor] Save Error: {e}")


# === Detect Reboot ===
def detect_reboot(dispatcher):
    data = load_last_status()
    last_boot = data.get("last_boot")

    current_boot = datetime.now().isoformat()
    data["last_boot"] = current_boot
    save_last_status(data)

    # If there was a previous record, calculate uptime diff
    if last_boot:
        try:
            last_time = datetime.fromisoformat(last_boot)
            diff = datetime.now() - last_time
            hours, remainder = divmod(diff.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{int(hours)}h {int(minutes)}m"
        except Exception:
            uptime_str = "unknown"
    else:
        uptime_str = "unknown"

    # Compose reboot alert
    reboot_msg = (
        f"⚡ <b>WENBNB Neural Engine Reboot Detected!</b>\n"
        f"🕒 <b>Previous Uptime:</b> {uptime_str}\n"
        f"💻 <b>Platform:</b> {platform.system()} {platform.release()}\n"
        f"🧠 <b>Status:</b> All systems reinitialized successfully.\n\n"
        f"{BRAND_TAG}"
    )

    # Notify all admins 💌
    for admin in ADMIN_IDS:
        try:
            dispatcher.bot.send_message(admin, reboot_msg, parse_mode="HTML")
        except Exception as e:
            print(f"[RebootMonitor] Failed to notify admin: {e}")


# === Manual Check Command ===
def reboot_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admins can check reboot info.")
    data = load_last_status()
    msg = (
        f"🧩 <b>Reboot Monitor</b>\n"
        f"🕒 Last Boot Recorded: <b>{data.get('last_boot', 'N/A')}</b>\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")


# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("reboot", reboot_status))
    detect_reboot(dp)
    print("⚡ WENBNB Reboot Monitor v8.6-R initialized.")
