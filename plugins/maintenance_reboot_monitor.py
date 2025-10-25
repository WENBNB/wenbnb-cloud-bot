"""
WENBNB Reboot Monitor v1.8-Pro — Self-Aware Uptime Tracker
────────────────────────────────────────────────────────────
Monitors and records every system reboot, syncs with maintenance_core telemetry,
and alerts admin automatically on restart.

💫 Powered by WENBNB Neural Engine — Resilience Awareness Framework 24×7 ⚡
"""

import os, json, time, threading
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

REBOOT_FILE = "data/last_reboot.json"
ADMIN_IDS = [5698007588]       # ← your Telegram ID
BRAND_TAG = "💫 WENBNB Neural Engine — Resilience Awareness 24×7 ⚡"
CHECK_INTERVAL = 3600          # verify uptime every hour


# === UTILITIES ===
def log(msg):
    print(f"[RebootMonitor] {msg}")


def record_reboot():
    """Record a new reboot timestamp."""
    try:
        os.makedirs("data", exist_ok=True)
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origin": "Render/Auto-Init"
        }
        with open(REBOOT_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log(f"🔁 Recorded reboot at {data['timestamp']}")
        return data
    except Exception as e:
        log(f"Error recording reboot: {e}")
        return None


def get_last_reboot():
    """Return last recorded reboot time."""
    try:
        if os.path.exists(REBOOT_FILE):
            with open(REBOOT_FILE, "r") as f:
                return json.load(f)
        return None
    except Exception as e:
        log(f"Error reading reboot file: {e}")
        return None


# === BACKGROUND MONITOR ===
def uptime_watcher(bot):
    """Periodically confirm uptime & reboot trace."""
    while True:
        try:
            last = get_last_reboot()
            if not last:
                record_reboot()
            else:
                ts = last.get("timestamp")
                log(f"Heartbeat OK — last reboot logged at {ts}")
        except Exception as e:
            log(f"[UptimeWatcher Error] {e}")
        time.sleep(CHECK_INTERVAL)


# === TELEGRAM COMMANDS ===
def reboot_status(update: Update, context: CallbackContext):
    """Show the most recent reboot info."""
    data = get_last_reboot()
    if not data:
        update.message.reply_text("⚙️ No reboot data found yet.")
        return
    msg = (
        f"🔁 <b>Last Reboot Logged</b>\n"
        f"🕒 <b>Time:</b> {data['timestamp']}\n"
        f"📡 <b>Source:</b> {data['origin']}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")


# === REGISTER WITH BOT CORE ===
def register_handlers(dp):
    """Register handlers and start monitoring thread."""
    record = record_reboot()
    for admin in ADMIN_IDS:
        try:
            dp.bot.send_message(
                admin,
                f"⚡ <b>WENBNB Reboot Detected</b>\n"
                f"🕒 {record['timestamp']}\n"
                f"📡 Source: {record['origin']}\n\n"
                f"{BRAND_TAG}",
                parse_mode="HTML",
            )
        except Exception as e:
            log(f"DM failed: {e}")

    dp.add_handler(CommandHandler("rebootlog", reboot_status))

    threading.Thread(target=uptime_watcher, args=(dp.bot,), daemon=True).start()
    log("💫 WENBNB Reboot Monitor v1.8-Pro initialized (Render + Local compatible).")
