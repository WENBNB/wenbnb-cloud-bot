"""
WENBNB Plugin Manager v8.5 Ultra-Safe — Dynamic Neural Loader + Self-Healing Sync
──────────────────────────────────────────────────────────────────────────────────
Purpose:
• Dynamically load, reload, and validate all /plugins modules
• Dual compatibility for register() & register_handlers()
• Self-healing reimport with clean cache handling
• Auto-verifies each plugin post-load and logs integration
• Emotion-sync safe for Neural Engine 8.x builds

💫 Powered by WENBNB Neural Engine — Modular Intelligence 24×7 ⚡
"""

import importlib, os, sys, traceback, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLUGIN_DIR = "plugins"
ACTIVE_PLUGINS = {}
FAILED_PLUGINS = {}
ADMIN_IDS = [5698007588]  # Replace with your Telegram ID
BRAND_TAG = "💫 WENBNB Neural Engine — Modular Intelligence 24×7 ⚡"


# === Logging ===
def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[WENBNB | PluginManager | {ts}] {msg}")


# === Plugin Loader ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []

    log("🚀 Initializing full plugin load cycle...")
    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"{PLUGIN_DIR}.{module_name}"

            try:
                # 🧠 Clear old imports
                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                # Dual compatibility check
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register_handlers()"
                elif hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register()"
                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No entry function found"
                    log(f"⚠️ {module_name}: No register() or register_handlers() found.")

                loaded.append(module_name)
                log(f"✅ Loaded plugin: {module_name}")

            except Exception as e:
                err_msg = str(e).split("\n")[0]
                FAILED_PLUGINS[module_name] = err_msg
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {err_msg}"
                failed.append((module_name, err_msg))
                log(f"❌ Error loading {module_name}: {err_msg}")

    # Summary
    log(f"✅ Total Loaded: {len(loaded)} | ❌ Failed: {len(failed)}")
    if failed:
        log(f"⚠️ Failed Modules → {', '.join([x[0] for x in failed])}")

    # Safety check delay
    time.sleep(1.5)
    validate_plugin_integrity()
    return loaded, failed


# === Validate Integration ===
def validate_plugin_integrity():
    """Ensure active plugin modules exist and expose expected functions."""
    for name in list(ACTIVE_PLUGINS.keys()):
        path = f"{PLUGIN_DIR}.{name}"
        try:
            module = sys.modules.get(path)
            if not module:
                ACTIVE_PLUGINS[name] = "⚠️ Missing in memory"
            elif not any(hasattr(module, fn) for fn in ["register", "register_handlers"]):
                ACTIVE_PLUGINS[name] = "⚠️ Invalid module structure"
        except Exception as e:
            ACTIVE_PLUGINS[name] = f"⚠️ Validation Error: {e}"


# === Auto Recovery ===
def attempt_recover(dispatcher):
    if not FAILED_PLUGINS:
        return
    log("🩺 Attempting auto-recovery for failed plugins...")

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
        log(f"✨ Recovery Success — {len(recovered)} plugins reloaded.")
    else:
        log("💤 No recoverable plugins found.")


# === /modules ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check module status.")
        return

    text = "🧩 <b>WENBNB Plugin Status — v8.5</b>\n\n"
    for name, status in sorted(ACTIVE_PLUGINS.items()):
        if "✅" in status:
            icon = "🟢"
        elif "⚠️" in status:
            icon = "🟡"
        else:
            icon = "🔴"
        text += f"{icon} <b>{name}</b>: {status}\n"

    if FAILED_PLUGINS:
        text += "\n🔻 <b>Failed Modules:</b>\n"
        for name, err in FAILED_PLUGINS.items():
            text += f"❌ <b>{name}</b>: {err}\n"

    text += f"\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")


# === /reload ===
def reload_plugins(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can reload modules.")
        return

    from wenbot import dp
    ACTIVE_PLUGINS.clear()
    FAILED_PLUGINS.clear()

    update.message.reply_text("🔄 Reloading all plugins...", parse_mode="HTML")
    loaded, failed = load_all_plugins(dp)
    attempt_recover(dp)

    summary = (
        f"✅ <b>Loaded:</b> {len(loaded)}\n"
        f"⚠️ <b>Failed:</b> {len(failed)}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(summary, parse_mode="HTML")


# === Error Handler ===
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


# === Register ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    dp.add_error_handler(plugin_error_handler)
    log("💫 PluginManager v8.5 Ultra-Safe initialized — Handler ready.")
