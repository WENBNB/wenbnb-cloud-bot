"""
WENBNB Maintenance Suite v8.1-Pro — Unified Self-Healing + Reboot Intelligence
───────────────────────────────────────────────────────────────────────────────
Combines:
• Full maintenance_core (telemetry, backup, S3 optional)
• Reboot monitor + uptime awareness
• Integrated telemetry sync + admin DM alerts

💫 Powered by WENBNB Neural Engine — Integrity, Resilience & Awareness 24×7 ⚡
"""

import os, time, json, threading, zipfile, traceback, psutil, platform
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

# === CONFIG ===
ADMIN_IDS = [5698007588]      # ← your Telegram ID
BACKUP_DIR = "backups"
LOGS_DIR = "logs"
DATA_DIR = "data"
ANALYTICS_FILE = os.path.join(DATA_DIR, "telemetry.json")
REBOOT_FILE = os.path.join(DATA_DIR, "last_reboot.json")

BRAND_TAG = "💫 WENBNB Neural Engine — Integrity & Awareness 24×7 ⚡"
CHECK_INTERVAL = 86400   # backup/telemetry every 24h
UPTIME_CHECK_INTERVAL = 3600  # reboot heartbeat hourly

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


# === BASIC UTIL ===
def log(msg):
    print(f"[MaintenancePro] {msg}")


# === TELEMETRY CORE ===
def record_telemetry(event, data=None):
    try:
        analytics = {}
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, "r") as f:
                analytics = json.load(f)

        analytics.setdefault(event, []).append({
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        })

        with open(ANALYTICS_FILE, "w") as f:
            json.dump(analytics, f, indent=2)

        log(f"📊 Telemetry recorded: {event}")
    except Exception as e:
        log(f"[Telemetry Error] {e}")


# === REBOOT TELEMETRY + MONITOR ===
def record_reboot_event(source="Render/Auto-Init"):
    """Log reboot in telemetry + JSON record."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        reboot_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source
        }
        with open(REBOOT_FILE, "w") as f:
            json.dump(reboot_data, f, indent=2)

        record_telemetry("reboot_events", reboot_data)
        log(f"🔁 Reboot event recorded: {reboot_data}")
        return reboot_data
    except Exception as e:
        log(f"[Reboot Log Error] {e}")
        return None


def get_last_reboot():
    try:
        if os.path.exists(REBOOT_FILE):
            with open(REBOOT_FILE, "r") as f:
                return json.load(f)
        return None
    except Exception as e:
        log(f"[Reboot Read Error] {e}")
        return None


def uptime_watcher(bot):
    """Background monitor that confirms uptime & logs if missing."""
    while True:
        try:
            last = get_last_reboot()
            if not last:
                record_reboot_event("Initial Start")
            else:
                log(f"Heartbeat OK — last reboot at {last.get('timestamp')}")
        except Exception as e:
            log(f"[Uptime Watch Error] {e}")
        time.sleep(UPTIME_CHECK_INTERVAL)


# === BACKUP ENGINE ===
def create_backup_archive():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = os.path.join(BACKUP_DIR, f"WENBNB_Backup_{ts}.zip")
    try:
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for folder in [LOGS_DIR, DATA_DIR]:
                for root, _, files in os.walk(folder):
                    for f in files:
                        path = os.path.join(root, f)
                        z.write(path, os.path.relpath(path, os.getcwd()))
        log(f"💾 Created backup archive: {archive}")
        return archive
    except Exception as e:
        log(f"[Backup Error] {e}")
        return None


# === SYSTEM HEALTH REPORT ===
def system_health_report():
    try:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "platform": f"{platform.system()} {platform.release()}"
        }
    except Exception as e:
        return {"error": str(e)}


# === MAIN MAINTENANCE THREAD ===
def maintenance_daemon(bot):
    while True:
        try:
            health = system_health_report()
            record_telemetry("system_health", health)
            archive = create_backup_archive()

            msg = (
                "🧠 <b>Maintenance Report</b>\n"
                f"💾 Backup: {os.path.basename(archive) if archive else 'failed'}\n"
                f"💻 CPU: {health.get('cpu', '?')}%\n"
                f"📈 RAM: {health.get('ram', '?')}%\n"
                f"💿 Disk: {health.get('disk', '?')}%\n"
                f"⚙️ Platform: {health.get('platform', '?')}\n\n"
                f"{BRAND_TAG}"
            )

            for admin in ADMIN_IDS:
                bot.send_message(admin, msg, parse_mode="HTML")

        except Exception as e:
            for admin in ADMIN_IDS:
                bot.send_message(admin, f"⚠️ Maintenance Error: <code>{e}</code>", parse_mode="HTML")
            log(f"[Maintenance Error] {traceback.format_exc()}")

        time.sleep(CHECK_INTERVAL)


# === COMMANDS ===
def backup_now(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admins can run manual backups.")
    update.message.reply_text("⏳ Creating manual backup...")
    archive = create_backup_archive()
    if archive:
        update.message.reply_document(open(archive, "rb"))
        update.message.reply_text(f"✅ Manual backup complete!\n{BRAND_TAG}")
    else:
        update.message.reply_text("⚠️ Backup failed.")


def telemetry_report(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admins can view analytics.")
    if not os.path.exists(ANALYTICS_FILE):
        return update.message.reply_text("📊 No telemetry data yet.")
    with open(ANALYTICS_FILE) as f:
        analytics = json.load(f)
    msg = (
        f"📈 <b>Telemetry Summary</b>\n\n"
        f"🪪 Events Tracked: <b>{len(analytics.keys())}</b>\n"
        f"💾 Stored in telemetry.json\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")


def reboot_status(update: Update, context: CallbackContext):
    """Show last reboot info to admin."""
    data = get_last_reboot()
    if not data:
        update.message.reply_text("⚙️ No reboot data recorded yet.")
        return
    msg = (
        f"🔁 <b>Last Reboot</b>\n"
        f"🕒 Time: {data['timestamp']}\n"
        f"📡 Source: {data['source']}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")


# === REGISTER HANDLERS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("backup", backup_now))
    dp.add_handler(CommandHandler("telemetry", telemetry_report))
    dp.add_handler(CommandHandler("rebootlog", reboot_status))

    record = record_reboot_event("Render/Auto-Init")
    for admin in ADMIN_IDS:
        try:
            dp.bot.send_message(
                admin,
                f"⚡ <b>WENBNB Reboot Detected</b>\n"
                f"🕒 {record['timestamp']}\n"
                f"📡 Source: {record['source']}\n\n"
                f"{BRAND_TAG}",
                parse_mode="HTML"
            )
        except Exception as e:
            log(f"[Admin Notify Error] {e}")

    threading.Thread(target=uptime_watcher, args=(dp.bot,), daemon=True).start()
    threading.Thread(target=maintenance_daemon, args=(dp.bot,), daemon=True).start()
    log("💎 Maintenance Suite v8.1-Pro initialized — telemetry + reboot sync active.")
