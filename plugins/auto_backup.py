"""
WENBNB Auto-Backup & Error Log Archiver v1.0
Backs up system logs, user data, and critical AI memory daily
🚀 Powered by WENBNB Neural Engine — Data Integrity Layer 24×7
"""

import os, time, threading, zipfile, shutil, traceback
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [123456789]  # Replace with your Telegram ID
BACKUP_DIR = "backups"
LOGS_DIR = "logs"
DATA_DIR = "data"
CHECK_INTERVAL = 86400  # 24 hours
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Data Integrity Layer 24×7"


# === Ensure directories exist ===
for d in [BACKUP_DIR, LOGS_DIR, DATA_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)


def create_backup_archive():
    """Create timestamped ZIP archive of logs + data"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = os.path.join(BACKUP_DIR, f"WENBNB_Backup_{timestamp}.zip")
        with zipfile.ZipFile(backup_name, "w", zipfile.ZIP_DEFLATED) as backup_zip:
            for folder in [LOGS_DIR, DATA_DIR]:
                for root, _, files in os.walk(folder):
                    for file in files:
                        path = os.path.join(root, file)
                        arcname = os.path.relpath(path, start=os.getcwd())
                        backup_zip.write(path, arcname)
        print(f"[Backup] Created archive: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"[Backup Error] {e}")
        return None


def cleanup_old_backups(max_keep=5):
    """Keep only the newest 5 backups"""
    try:
        files = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)], key=os.path.getmtime)
        if len(files) > max_keep:
            for old_file in files[:-max_keep]:
                os.remove(old_file)
                print(f"[Cleanup] Removed old backup: {old_file}")
    except Exception as e:
        print(f"[Cleanup Error] {e}")


def backup_thread(bot):
    """Thread that runs continuous backup every 24h"""
    while True:
        try:
            archive = create_backup_archive()
            cleanup_old_backups()
            if archive:
                for admin_id in ADMIN_IDS:
                    bot.send_message(
                        admin_id,
                        f"✅ Daily Backup Completed\n🗂️ File: <b>{os.path.basename(archive)}</b>\n\n{BRAND_TAG}",
                        parse_mode="HTML"
                    )
        except Exception as e:
            error_log = traceback.format_exc()
            print(f"[Backup Thread Error] {error_log}")
            for admin_id in ADMIN_IDS:
                bot.send_message(admin_id, f"⚠️ Backup Error:\n<code>{e}</code>", parse_mode="HTML")
        time.sleep(CHECK_INTERVAL)


# === Manual Command ===
def backup_now(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can run manual backup.")
        return
    update.message.reply_text("⏳ Creating manual backup...")
    archive = create_backup_archive()
    if archive:
        update.message.reply_document(open(archive, "rb"))
        update.message.reply_text(f"✅ Manual backup complete!\n{BRAND_TAG}")
    else:
        update.message.reply_text("⚠️ Backup failed. Check logs.")


# === Register Handlers ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("backup", backup_now))
    threading.Thread(target=backup_thread, args=(dp.bot,), daemon=True).start()
    print("💾 Auto-Backup thread started.")
