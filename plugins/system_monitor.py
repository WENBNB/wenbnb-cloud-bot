"""
WENBNB System Monitor v8.4-Pro — Neural Heartbeat + Auto-Heal Guardian
──────────────────────────────────────────────────────────────────────
Purpose:
• Real-time system health metrics (CPU, RAM, uptime, API)
• Intelligent plugin auto-recovery with unified logging
• Sends heartbeat updates to dashboard (if configured)
• Emotion-aware notifications (soft alert mode)

💫 Powered by WENBNB Neural Engine — Resilience Framework 24×7
"""

import os, time, threading, requests, traceback, platform, psutil, importlib
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
ADMIN_IDS = [123456789]  # Replace with your admin ID
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

FAILED_PLUGINS = {}
STOP_FLAG = False
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "")


# === LOGGING ===
def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[WENBNB | SystemMonitor | {ts}] {msg}")


# === DASHBOARD SYNC ===
def send_dashboard_ping(event: str, data=None):
    if not DASHBOARD_URL:
        return
    try:
        payload = {"event": event, "time": int(time.time()), "data": data or {}}
        requests.post(DASHBOARD_URL.rstrip("/") + "/update_activity", json=payload, timeout=5)
    except Exception:
        pass


# === AUTO-HEAL CORE ===
def auto_heal_plugins(dispatcher):
    while not STOP_FLAG:
        try:
            for file in os.listdir(PLUGIN_DIR):
                if not file.endswith(".py") or file.startswith("__"):
                    continue

                module_name = file[:-3]
                if module_name in FAILED_PLUGINS:
                    try:
                        module_path = f"{PLUGIN_DIR}.{module_name}"
                        if module_path in sys.modules:
                            del sys.modules[module_path]
                        module = importlib.import_module(module_path)

                        if hasattr(module, "register_handlers"):
                            module.register_handlers(dispatcher)
                        elif hasattr(module, "register"):
                            module.register(dispatcher)

                        del FAILED_PLUGINS[module_name]
                        log(f"💚 Auto-recovered plugin: {module_name}")
                        for admin_id in ADMIN_IDS:
                            dispatcher.bot.send_message(
                                admin_id,
                                f"🛠️ <b>Auto-Healed:</b> {module_name}",
                                parse_mode="HTML"
                            )
                        send_dashboard_ping("plugin_recovered", {"plugin": module_name})
                    except Exception as e:
                        log(f"⚠️ Auto-heal retry failed for {module_name}: {e}")
            time.sleep(300)
        except Exception as e:
            log(f"[AutoHeal Error] {e}")
            time.sleep(300)


# === SYSTEM HEARTBEAT MONITOR ===
def monitor_system(dispatcher):
    global SYSTEM_STATUS
    while not STOP_FLAG:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            uptime_seconds = (datetime.now() - BOT_START_TIME).total_seconds()
            hours, remainder = divmod(int(uptime_seconds), 3600)
            minutes, _ = divmod(remainder, 60)

            # API heartbeat
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
                        "⚠️ <b>Binance API appears DOWN!</b>\nSwitching to Watch Mode 🌙",
                        parse_mode="HTML"
                    )
                send_dashboard_ping("api_down")

            send_dashboard_ping("heartbeat", SYSTEM_STATUS)

        except Exception as e:
            log(f"[SystemMonitor Error] {traceback.format_exc()}")
        time.sleep(CHECK_INTERVAL)


# === START THREADS ===
def start_monitor(dispatcher):
    threading.Thread(target=monitor_system, args=(dispatcher,), daemon=True).start()
    threading.Thread(target=auto_heal_plugins, args=(dispatcher,), daemon=True).start()
    log("🧠 System Monitor threads started (Heartbeat + Auto-Heal).")


# === STATUS COMMAND ===
def system_status(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check system status.")
        return

    s = SYSTEM_STATUS
    text = (
        f"🧩 <b>WENBNB System Monitor v8.4-Pro</b>\n\n"
        f"🕒 Uptime: <b>{s['uptime']}</b>\n"
        f"💻 CPU Usage: <b>{s['cpu']}%</b>\n"
        f"📈 RAM Usage: <b>{s['ram']}%</b>\n"
        f"🌐 API Health: {s['api']}\n"
        f"🩺 Auto-Heal: {s['autoheal']}\n"
        f"⚙️ Platform: {platform.system()} {platform.release()}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("system", system_status))
    start_monitor(dp)
    log("💫 System Monitor registered successfully.")
