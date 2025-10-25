"""
WENBNB Plugin Manager v8.6-Pro++ — Emotion-Safe + Render Optimized
────────────────────────────────────────────────────────────────────────────────
Purpose:
• Dynamically load, reload, and validate all /plugins modules
• Auto-detects maintenance_pro telemetry
• Compatible with register() & register_handlers()
• Self-healing reload without circular imports (Render-safe)
• Emotion-Sync protected for Neural Engine 8.x

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

# === LOGGING ===
def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[WENBNB | PluginManager | {ts}] {msg}")

# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []

    log("🚀 Neural Plugin Loader initiated.")
    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"{PLUGIN_DIR}.{module_name}"

            try:
                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                # Compatibility: register_handlers() or register()
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register_handlers()"
                elif hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register()"
                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No entry function found"
                    log(f"⚠️ {module_name}: Missing register or register_handlers().")

                loaded.append(module_name)
                log(f"✅ Loaded plugin: {module_name}")

                # Maintenance Suite Check
                if module_name == "maintenance_pro":
                    log("🧠 Maintenance Suite detected — verifying telemetry sync.")
                    try:
                        if hasattr(module, "get_last_reboot"):
                            result = module.get_last_reboot()
                            status = result.get("timestamp") if result else "No data"
                            log(f"💾 Maintenance telemetry active (Last reboot: {status})")
                            ACTIVE_PLUGINS[module_name] += " 🩵 (Telemetry OK)"
                        else:
                            log("⚠️ maintenance_pro missing get_last_reboot() function.")
                    except Exception as e:
                        log(f"⚠️ maintenance_pro check failed: {e}")

            except Exception as e:
                err_msg = str(e).split("\n")[0]
                FAILED_PLUGINS[module_name] = err_msg
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {err_msg}"
                failed.append((module_name, err_msg))
                log(f"❌ Error loading {module_name}: {err_msg}")

    log(f"✅ Total Loaded: {len(loaded)} | ❌ Failed: {len(failed)}")
    if failed:
        log(f"⚠️ Failed → {', '.join([x[0] for x in failed])}")
    time.sleep(1.2)
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
    log("🩺 Auto-recovery process running...")

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
            log(f"💚 Auto-recovered: {name}")
        except Exception as e:
            log(f"⚠️ Still failing {name}: {e}")

    if recovered:
        log(f"✨ Recovered {len(recovered)} plugin(s).")
    else:
        log("💤 No recoverable modules at this time.")


# === /modules ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check module status.")
        return

    text = "🧩 <b>WENBNB Plugin Status — v8.6-Pro++</b>\n\n"
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

    text += f"\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")


# === /reload ===
def reload_plugins(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can reload modules.")
        return

    dispatcher = context.dispatcher  # ✅ FIXED: use active dispatcher (no dp import)
    ACTIVE_PLUGINS.clear()
    FAILED_PLUGINS.clear()
    update.message.reply_text("🔄 Reloading all plugins...", parse_mode="HTML")

    loaded, failed = load_all_plugins(dispatcher)
    attempt_recover(dispatcher)

    if "maintenance_pro" in ACTIVE_PLUGINS:
        update.message.reply_text("🧠 Maintenance Suite verified & active 💫", parse_mode="HTML")

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
        log(f"[Plugin Error] {e}\n{trace}")
        if update and update.effective_user:
            update.message.reply_text(
                f"⚠️ Neural Core Error:\n<code>{str(e)}</code>", parse_mode="HTML"
            )


# === REGISTER HANDLERS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    dp.add_error_handler(plugin_error_handler)
    log("💫 PluginManager v8.6-Pro++ initialized — maintenance-aware & Render-safe.")
