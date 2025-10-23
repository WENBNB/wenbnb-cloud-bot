"""
WENBNB Maintenance Core v3.0
Unified system for auto-backup, analytics, and health monitoring.
🚀 Powered by WENBNB Neural Engine — Integrity & Insight Layer 24×7
"""

import os, time, threading, zipfile, shutil, traceback, psutil, json
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [123456789]  # replace with your Telegram ID
BACKUP_DIR = "backups"
LOGS_DIR = "logs"
DATA_DIR = "data"
ANALYTICS_FILE = os.path.join(DATA_DIR, "telemetry.json")
CHECK_INTERVAL = 86400  # daily cycle
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Integrity & Insight Layer 24×7"


# === ensure dirs ===
for d in [BACKUP_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)


# === BACKUP ===
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
        print(f"[Backup] created {archive}")
        return archive
    except Exception as e:
        print(f"[Backup Error] {e}")
        return None


def cleanup_backups(limit=5):
    files = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)], key=os.path.getmtime)
    for old in files[:-limit]:
        os.remove(old)
        print(f"[Cleanup] removed {old}")


# === TELEMETRY ===
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
    except Exception as e:
        print(f"[Telemetry Error] {e}")


def system_health_report():
    try:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "mem": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "uptime": time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))
        }
    except Exception as e:
        return {"error": str(e)}


# === BACKGROUND LOOP ===
def maintenance_daemon(bot):
    while True:
        try:
            # health check
            health = system_health_report()
            record_telemetry("system_health", health)

            # backup
            archive = create_backup_archive()
            cleanup_backups()

            # notify admins
            msg = (
                "🧠 <b>WENBNB Maintenance Report</b>\n"
                f"💾 Backup: {os.path.basename(archive) if archive else 'failed'}\n"
                f"⚙️ CPU: {health.get('cpu', '?')}%\n"
                f"💻 RAM: {health.get('mem', '?')}%\n"
                f"💿 Disk: {health.get('disk', '?')}%\n\n"
                f"{BRAND_TAG}"
            )
            for admin in ADMIN_IDS:
                bot.send_message(admin, msg, parse_mode="HTML")

        except Exception as e:
            trace = traceback.format_exc()
            print(f"[Maintenance Error] {trace}")
            for admin in ADMIN_IDS:
                bot.send_message(admin, f"⚠️ Maintenance Error:\n<code>{e}</code>", parse_mode="HTML")

        time.sleep(CHECK_INTERVAL)


# === COMMANDS ===
def backup_now(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admins can use this command.")
    update.message.reply_text("⏳ Creating manual backup...")
    archive = create_backup_archive()
    if archive:
        update.message.reply_document(open(archive, "rb"))
        update.message.reply_text(f"✅ Manual backup complete!\n{BRAND_TAG}")
    else:
        update.message.reply_text("⚠️ Backup failed. Check logs.")


def telemetry_report(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admins can view analytics.")
    try:
        if not os.path.exists(ANALYTICS_FILE):
            update.message.reply_text("📊 No analytics recorded yet.")
            return
        with open(ANALYTICS_FILE) as f:
            analytics = json.load(f)
        msg = f"📈 <b>Telemetry Summary</b>\n\nEvents tracked: {len(analytics.keys())}\n{BRAND_TAG}"
        update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error loading analytics: {e}")


# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("backup", backup_now))
    dp.add_handler(CommandHandler("telemetry", telemetry_report))
    threading.Thread(target=maintenance_daemon, args=(dp.bot,), daemon=True).start()
    print("🧠 Maintenance Core active.")
