"""
WENBNB Maintenance Core v8.4-Pro — Neural Auto-Integrity & Backup Engine
────────────────────────────────────────────────────────────────────────────
Purpose:
• Scheduled system health checks, backup creation, and S3 sync
• Cross-syncs with System Monitor (auto-heal alerts)
• Generates telemetry and sends daily admin reports
🚀 Powered by WENBNB Neural Engine — Integrity & Insight Layer 24×7
"""

import os, time, threading, zipfile, json, traceback, psutil, boto3
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [5698007588]  # replace with your Telegram ID
BACKUP_DIR = "backups"
LOGS_DIR = "logs"
DATA_DIR = "data"
ANALYTICS_FILE = os.path.join(DATA_DIR, "telemetry.json")
CHECK_INTERVAL = 86400  # every 24h
BRAND_TAG = "🚀 WENBNB Neural Engine — Integrity & Insight Layer 24×7 ⚡"

# === S3 CONFIG ===
S3_ENABLED = os.getenv("S3_ENABLED", "true").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")

if S3_ENABLED:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
        )
    except Exception as e:
        print(f"[S3 Init Error] {e}")
        s3_client = None
else:
    s3_client = None

for d in [BACKUP_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)


# === UTILITIES ===
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
        return archive
    except Exception as e:
        print(f"[Backup Error] {e}")
        return None


def upload_to_s3(file_path, folder="backups"):
    if not s3_client or not S3_BUCKET:
        return False
    try:
        key = f"{folder}/{os.path.basename(file_path)}"
        s3_client.upload_file(file_path, S3_BUCKET, key)
        print(f"[S3] Uploaded: {key}")
        return True
    except Exception as e:
        print(f"[S3 Upload Error] {e}")
        return False


def record_telemetry(event, data=None):
    try:
        analytics = {}
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, "r") as f:
                analytics = json.load(f)
        analytics.setdefault(event, []).append({
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
        })
        with open(ANALYTICS_FILE, "w") as f:
            json.dump(analytics, f, indent=2)

        if S3_ENABLED and s3_client:
            upload_to_s3(ANALYTICS_FILE, folder="telemetry")
    except Exception as e:
        print(f"[Telemetry Error] {e}")


def system_health_report():
    try:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "mem": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "uptime": f"{int(time.time() - psutil.boot_time()) // 3600}h",
        }
    except Exception as e:
        return {"error": str(e)}


# === MAIN LOOP ===
def maintenance_daemon(bot):
    while True:
        try:
            health = system_health_report()
            record_telemetry("system_health", health)
            archive = create_backup_archive()
            if archive:
                upload_to_s3(archive)
            msg = (
                "🧠 <b>Neural Maintenance Summary</b>\n"
                f"🕒 Uptime: {health.get('uptime','?')}\n"
                f"💻 CPU: {health.get('cpu','?')}%\n"
                f"📈 RAM: {health.get('mem','?')}%\n"
                f"💾 Disk: {health.get('disk','?')}%\n"
                f"💾 Backup: {os.path.basename(archive) if archive else 'failed'}\n\n"
                f"{BRAND_TAG}"
            )
            for admin in ADMIN_IDS:
                bot.send_message(admin, msg, parse_mode="HTML")
        except Exception as e:
            trace = traceback.format_exc()
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
        upload_to_s3(archive)
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
        msg = (
            f"📈 <b>Telemetry Summary</b>\n\n"
            f"Tracked events: <b>{len(analytics.keys())}</b>\n"
            f"Latest: {list(analytics.keys())[-1] if analytics else 'None'}\n\n"
            f"{BRAND_TAG}"
        )
        update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error loading analytics: {e}")


# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("backup", backup_now))
    dp.add_handler(CommandHandler("telemetry", telemetry_report))
    threading.Thread(target=maintenance_daemon, args=(dp.bot,), daemon=True).start()
    print("🧠 Maintenance Core v8.4-Pro (Auto-Telemetry + S3) active.")
