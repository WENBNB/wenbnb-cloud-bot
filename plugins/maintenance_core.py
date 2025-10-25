"""
WENBNB Maintenance Core v8.5L — Local Integrity Engine (No S3)
───────────────────────────────────────────────────────────────
Purpose:
• Self-healing + daily telemetry logging
• Smart zip-based local backup (no cloud)
• /backup and /telemetry admin commands
• Seamless auto-registration with Plugin Manager

💫 Powered by WENBNB Neural Engine — Integrity & Insight Layer 24×7 ⚡
"""

import os, time, threading, zipfile, json, traceback, psutil
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [5698007588]  # Replace with your Telegram ID
BACKUP_DIR = "backups"
LOGS_DIR = "logs"
DATA_DIR = "data"
ANALYTICS_FILE = os.path.join(DATA_DIR, "telemetry.json")
CHECK_INTERVAL = 86400  # every 24 hours
BRAND_TAG = "💫 WENBNB Neural Engine — Local Integrity Layer 24×7 ⚡"

# === ensure dirs ===
for d in [BACKUP_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# === Backup Creator ===
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
        print(f"[Backup Created] {archive}")
        return archive
    except Exception as e:
        print(f"[Backup Error] {e}")
        return None

# === Telemetry Recorder ===
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
        print(f"[Telemetry Updated] Event: {event}")
    except Exception as e:
        print(f"[Telemetry Error] {e}")

# === System Health ===
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

# === Auto-Maintenance Thread ===
def maintenance_daemon(bot):
    while True:
        try:
            health = system_health_report()
            record_telemetry("system_health", health)
            archive = create_backup_archive()
            msg = (
                "🧠 <b>Maintenance Report</b>\n"
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
            for admin in ADMIN_IDS:
                bot.send_message(admin, f"⚠️ Maintenance Error:\n<code>{e}</code>", parse_mode="HTML")
        time.sleep(CHECK_INTERVAL)

# === Manual Backup Command ===
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

# === Telemetry Command ===
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

# === Register Handlers ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("backup", backup_now))
    dp.add_handler(CommandHandler("telemetry", telemetry_report))
    threading.Thread(target=maintenance_daemon, args=(dp.bot,), daemon=True).start()
    print("🧠 Maintenance Core v8.5L (Local Mode) active.")

# === Auto Register for Plugin Manager ===
def register(dp):
    try:
        register_handlers(dp)
        print("🧩 Maintenance Core successfully registered with PluginManager.")
    except Exception as e:
        print(f"[MaintenanceCore Register Error] {e}")
