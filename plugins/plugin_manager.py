"""
WENBNB Plugin Manager v8.4-Pro — Dynamic Neural Module Loader (Self-Healing + Emotion-Synced)
──────────────────────────────────────────────────────────────────────────────────────────────
Purpose:
• Auto-load and hot-reload all plugin modules under /plugins
• Clears import cache safely on reload
• Provides /modules and /reload admin control
• Includes auto-recovery + detailed logging

💫 Powered by WENBNB Neural Engine — Modular Intelligence Framework 24×7
"""

import importlib, os, sys, traceback, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLUGIN_DIR = "plugins"
ACTIVE_PLUGINS = {}
FAILED_PLUGINS = {}
ADMIN_IDS = [123456789]  # Replace with your real admin Telegram ID
BRAND_TAG = "💫 WENBNB Neural Engine — Modular Intelligence 24×7 ⚡"


# === LOGGING UTIL ===
def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[WENBNB | PluginManager | {ts}] {msg}")


# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []

    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"{PLUGIN_DIR}.{module_name}"

            try:
                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                # Dual compatibility: register() or register_handlers()
                if hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register()"
                elif hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register_handlers()"
                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No entry function found"
                    log(f"{module_name}: Missing register() or register_handlers().")

                loaded.append(module_name)
                log(f"✅ Loaded plugin: {module_name}")

            except Exception as e:
                error_summary = str(e).split("\n")[0]
                FAILED_PLUGINS[module_name] = error_summary
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {error_summary}"
                failed.append((module_name, error_summary))
                log(f"❌ Error loading {module_name}: {error_summary}")

    # Summary Logs
    log(f"✅ Successfully loaded: {len(loaded)} plugins")
    if failed:
        log(f"⚠️ Failed to load: {len(failed)} plugins → {', '.join([f[0] for f in failed])}")

    return loaded, failed


# === AUTO HEAL: TRY RELOAD ON FAIL ===
def attempt_recover(dispatcher):
    if not FAILED_PLUGINS:
        return

    log("🩺 Attempting auto-reload for failed plugins...")
    recovered = []

    for module_name in list(FAILED_PLUGINS.keys()):
        try:
            module_path = f"{PLUGIN_DIR}.{module_name}"
            if module_path in sys.modules:
                del sys.modules[module_path]

            module = importlib.import_module(module_path)
            if hasattr(module, "register_handlers"):
                module.register_handlers(dispatcher)
            elif hasattr(module, "register"):
                module.register(dispatcher)

            ACTIVE_PLUGINS[module_name] = "✅ Auto-Recovered"
            del FAILED_PLUGINS[module_name]
            recovered.append(module_name)
            log(f"💚 Auto-recovered plugin: {module_name}")

        except Exception as e:
            log(f"⚠️ Still failing: {module_name} → {e}")

    if recovered:
        log(f"✨ Recovered {len(recovered)} previously failed plugins.")
    else:
        log("💤 No recoverable plugins at this time.")


# === /modules STATUS ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check module status.")
        return

    text = "🧩 <b>WENBNB Plugin Status</b>\n\n"
    for name, status in ACTIVE_PLUGINS.items():
        text += f"• <b>{name}</b>: {status}\n"

    if FAILED_PLUGINS:
        text += "\n⚠️ <b>Failed Modules:</b>\n"
        for name, err in FAILED_PLUGINS.items():
            text += f"• <b>{name}</b>: {err}\n"

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
    update.message.reply_text("🔄 Reloading all plugins, please wait...", parse_mode="HTML")

    loaded, failed = load_all_plugins(dp)
    attempt_recover(dp)

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
        error_trace = "".join(traceback.format_exception(None, e, e.__traceback__))
        log(f"[Plugin Error] {e}\n{error_trace}")
        if update and update.effective_user:
            update.message.reply_text(
                f"⚠️ Neural Core Error:\n<code>{str(e)}</code>", parse_mode="HTML"
            )


# === REGISTER CORE COMMANDS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    dp.add_error_handler(plugin_error_handler)
    log("💫 PluginManager ready — monitoring plugin lifecycle.")
