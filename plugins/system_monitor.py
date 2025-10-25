"""
WENBNB System Monitor v8.4-Pro++ — Auto-Healing + Dual Command Support
────────────────────────────────────────────────────────────────────────────
Monitors CPU, RAM, uptime, and API health + maintains self-healing plugin sync.
Now includes:
• Dual command support (/status + /system)
• Heartbeat-aware monitoring threads
• Safe reboot telemetry access
💫 Powered by WENBNB Neural Engine — Resilience Framework 24×7 ⚡
"""

import time, threading, requests, traceback, platform, psutil, importlib, os, json
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [5698007588]  # Replace with your Telegram ID
PLUGIN_DIR = "plugins"
BOT_START_TIME = datetime.now()
CHECK_INTERVAL = 120  # seconds
BRAND_TAG = "💫 WENBNB Neural Engine — Resilience Framework 24×7 ⚡"

SYSTEM_STATUS = {
    "cpu": 0,
    "ram": 0,
    "uptime": "0h 0m",
    "api": "✅ OK",
    "autoheal": "✅ Active"
}

ACTIVE_PLUGINS = {}
STOP_FLAG = False


# === AUTO-HEALING CORE ===
def auto_heal_plugins(dispatcher):
    while not STOP_FLAG:
        try:
            for file in os.listdir(PLUGIN_DIR):
                if file.endswith(".py") and not file.startswith("__"):
                    module_name = file[:-3]
                    if module_name not in ACTIVE_PLUGINS or ACTIVE_PLUGINS[module_name] == "❌ Error":
                        try:
                            module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")
                            if hasattr(module, "register_handlers"):
                                module.register_handlers(dispatcher)
                                ACTIVE_PLUGINS[module_name] = "✅ Recovered"
                                print(f"[AutoHeal] Recovered {module_name}")
                                for admin_id in ADMIN_IDS:
                                    dispatcher.bot.send_message(
                                        admin_id,
                                        f"🛠️ Auto-Healed Plugin: <b>{module_name}</b>",
                                        parse_mode="HTML"
                                    )
                        except Exception as e:
                            print(f"[AutoHeal] Failed to reload {module_name}: {e}")
            time.sleep(300)
        except Exception as e:
            print(f"[AutoHeal Thread Error] {e}")
            time.sleep(300)


# === SYSTEM MONITOR ===
def monitor_system(dispatcher):
    global SYSTEM_STATUS
    while not STOP_FLAG:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            uptime_seconds = (datetime.now() - BOT_START_TIME).total_seconds()
            hours, remainder = divmod(int(uptime_seconds), 3600)
            minutes, _ = divmod(remainder, 60)

            try:
                res = requests.get("https://api.binance.com/api/v3/time", timeout=5)
                api_status = "✅ OK" if res.status_code == 200 else "⚠️ Slow"
            except Exception:
                api_status = "❌ Down"

            SYSTEM_STATUS.update({
                "cpu": cpu_usage,
                "ram": ram_usage,
                "uptime": f"{hours}h {minutes}m",
                "api": api_status
            })

            if api_status == "❌ Down":
                for admin_id in ADMIN_IDS:
                    dispatcher.bot.send_message(
                        admin_id,
                        "⚠️ <b>Binance API is DOWN!</b>\nSystem entering Watch Mode.",
                        parse_mode="HTML"
                    )

        except Exception as e:
            print(f"[SystemMonitor Error] {traceback.format_exc()}")
        time.sleep(CHECK_INTERVAL)


# === START MONITOR THREAD ===
def start_monitor(dispatcher):
    threading.Thread(target=monitor_system, args=(dispatcher,), daemon=True).start()
    threading.Thread(target=auto_heal_plugins, args=(dispatcher,), daemon=True).start()
    print("🧠 WENBNB System Monitor & Auto-Heal threads initialized.")


# === STATUS COMMANDS ===
def status_command(update: Update, context: CallbackContext):
    """Main system report command."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check system status.")
        return

    s = SYSTEM_STATUS
    reboot_file = "data/last_reboot.json"
    last_reboot = "N/A"
    try:
        if os.path.exists(reboot_file):
            with open(reboot_file, "r") as f:
                info = json.load(f)
                last_reboot = info.get("timestamp", "Unknown")
    except Exception as e:
        print(f"[Status] Failed to read last reboot time: {e}")

    text = (
        f"🧩 <b>WENBNB System Monitor v8.4-Pro++</b>\n\n"
        f"🕒 Uptime: <b>{s['uptime']}</b>\n"
        f"🔁 Last Reboot: <b>{last_reboot}</b>\n"
        f"💻 CPU Usage: <b>{s['cpu']}%</b>\n"
        f"📈 RAM Usage: <b>{s['ram']}%</b>\n"
        f"🌐 API Health: {s['api']}\n"
        f"🩺 Auto-Heal: {s['autoheal']}\n"
        f"⚙️ Platform: {platform.system()} {platform.release()}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def reboot_info(update: Update, context: CallbackContext):
    """Quick access to last reboot time."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can view reboot info.")
        return

    reboot_file = "data/last_reboot.json"
    if os.path.exists(reboot_file):
        with open(reboot_file, "r") as f:
            info = json.load(f)
            timestamp = info.get("timestamp", "Unknown")
    else:
        timestamp = "No data recorded yet."

    update.message.reply_text(f"🕓 <b>Last Reboot:</b> {timestamp}", parse_mode="HTML")


# === REGISTER HANDLERS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("system", status_command))  # ✅ Added alias
    dp.add_handler(CommandHandler("rebootinfo", reboot_info))
    start_monitor(dp)
    print("✅ System Monitor Handlers Registered — /status & /system ready.")
