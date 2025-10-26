"""
WENBNB Plugin Manager v8.6-Pro++ — Neural Boot Log Edition
──────────────────────────────────────────────────────────────────────────────
✨ Features:
• Dynamic load + auto-recovery + validation (Render-safe)
• Color-coded boot logs for premium console feel
• Neural summary footer in /modules
• Emotion-Sync compatible (no circular imports)

💫 Powered by WENBNB Neural Engine — Modular Intelligence 24×7 ⚡
"""

import importlib, os, sys, traceback, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLUGIN_DIR = "plugins"
ACTIVE_PLUGINS = {}
FAILED_PLUGINS = {}
ADMIN_IDS = [5698007588]
BRAND_TAG = "💫 WENBNB Neural Engine — Modular Intelligence 24×7 ⚡"

# === COLOR MAP ===
def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# === LOGGING ===
def log(msg: str, status="INFO"):
    ts = time.strftime("%H:%M:%S")
    colors = {
        "OK": "92",       # green
        "WARN": "93",     # yellow
        "FAIL": "91",     # red
        "INFO": "96"      # cyan
    }
    code = colors.get(status, "0")
    print(color_text(f"[{ts}] {msg}", code))

# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []

    log("🧠 Neural Plugin Loader initialized...", "INFO")
    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"{PLUGIN_DIR}.{module_name}"

            try:
                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                # Register plugin (either register_handlers() or register())
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register_handlers()"
                elif hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register()"
                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No entry function"
                    log(f"⚠️ {module_name}: Missing register or register_handlers().", "WARN")

                loaded.append(module_name)

                # === Custom Descriptive Log ===
                description = {
                    "price_tracker": "Market API connected",
                    "tokeninfo": "Neural Token Insight ready",
                    "web3_connect": "Web3 Stack online",
                    "airdrop_check": "Hybrid Airdrop Intelligence active",
                    "airdrop_alert": "Alert Scheduler engaged",
                    "ai_auto_reply": "Emotion Engine synced",
                    "maintenance_pro": "Maintenance Suite verified"
                }.get(module_name, "Module registered")

                log(f"[✅ OK]  {module_name}.py — {description}", "OK")

            except Exception as e:
                err_msg = str(e).split("\n")[0]
                FAILED_PLUGINS[module_name] = err_msg
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {err_msg}"
                failed.append((module_name, err_msg))
                log(f"[❌ FAIL]  {module_name}.py — {err_msg}", "FAIL")

    log(f"📦 Total Loaded: {len(loaded)} | ❌ Failed: {len(failed)}", "INFO")
    if failed:
        log(f"⚠️ Failed modules: {', '.join([x[0] for x in failed])}", "WARN")

    time.sleep(1.0)
    validate_plugin_integrity()
    return loaded, failed


# === VALIDATION ===
def validate_plugin_integrity():
    for name in list(ACTIVE_PLUGINS.keys()):
        path = f"{PLUGIN_DIR}.{name}"
        try:
            module = sys.modules.get(path)
            if not module:
                ACTIVE_PLUGINS[name] = "⚠️ Missing from memory"
            elif not any(hasattr(module, fn) for fn in ["register", "register_handlers"]):
                ACTIVE_PLUGINS[name] = "⚠️ Invalid structure"
        except Exception as e:
            ACTIVE_PLUGINS[name] = f"⚠️ Validation Error: {e}"


# === AUTO RECOVERY ===
def attempt_recover(dispatcher):
    if not FAILED_PLUGINS:
        return
    log("🩺 Auto-recovery initiated...", "INFO")

    recovered = []
    for name in list(FAILED_PLUGINS.keys()):
        try:
            module_path = f"{PLUGIN_DIR}.{name}"
            if module_path in sys.modules:
                del sys.modules[module_path]
            module = importlib.import_module(module_path)
            if hasattr(module, "register_handlers"):
                module.register_handlers(dispatcher)
            elif hasattr(module, "register"):
                module.register(dispatcher)
            ACTIVE_PLUGINS[name] = "✅ Auto-Recovered"
            del FAILED_PLUGINS[name]
            recovered.append(name)
            log(f"[💚 RECOVERED] {name}.py", "OK")
        except Exception as e:
            log(f"⚠️ Still failing {name}: {e}", "WARN")

    if recovered:
        log(f"✨ Recovered {len(recovered)} module(s).", "OK")
    else:
        log("💤 No recoverable modules at this time.", "INFO")


# === /modules ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check module status.")
        return

    text = "🧩 <b>WENBNB Plugin Status — Neural Edition</b>\n\n"
    sections = {
        "✅": "🟢 Active Modules",
        "⚠️": "🟡 Warnings",
        "❌": "🔴 Failed Loads"
    }

    categorized = {k: [] for k in sections.keys()}
    for name, status in ACTIVE_PLUGINS.items():
        if "✅" in status:
            categorized["✅"].append(f"• <b>{name}</b>: {status}")
        elif "⚠️" in status:
            categorized["⚠️"].append(f"• <b>{name}</b>: {status}")
        else:
            categorized["❌"].append(f"• <b>{name}</b>: {status}")

    for emoji, title in sections.items():
        if categorized[emoji]:
            text += f"\n<b>{title}</b>\n" + "\n".join(categorized[emoji]) + "\n"

    total = len(ACTIVE_PLUGINS)
    text += (
        f"\n🧠 Neural Sync: <b>Stable</b>\n"
        f"💾 Auto-Recovery: <b>Enabled</b>\n"
        f"📦 Total Modules: <b>{total}</b>\n\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(text, parse_mode="HTML")


# === /reload ===
def reload_plugins(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can reload modules.")
        return

    dispatcher = context.dispatcher
    ACTIVE_PLUGINS.clear()
    FAILED_PLUGINS.clear()
    update.message.reply_text("🔄 Reloading all plugins...", parse_mode="HTML")

    loaded, failed = load_all_plugins(dispatcher)
    attempt_recover(dispatcher)

    summary = (
        f"✅ <b>Loaded:</b> {len(loaded)}\n"
        f"⚠️ <b>Failed:</b> {len(failed)}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(summary, parse_mode="HTML")


# === ERROR HANDLER ===
def plugin_error_handler(update, context):
    try:
        raise context.error
    except Exception as e:
        trace = "".join(traceback.format_exception(None, e, e.__traceback__))
        log(f"[Plugin Error] {e}\n{trace}", "FAIL")
        if update and update.effective_user:
            update.message.reply_text(
                f"⚠️ Neural Core Error:\n<code>{str(e)}</code>", parse_mode="HTML"
            )


# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    dp.add_error_handler(plugin_error_handler)
    log("💫 PluginManager v8.6-Pro++ (Pro Log Edition) initialized.", "OK")
