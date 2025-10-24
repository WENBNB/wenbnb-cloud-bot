"""
WENBNB Plugin Manager v4.1 — Dynamic Neural Module Loader
Auto-loads all plugin modules, tracks health, and provides admin control via /modules
🚀 Powered by WENBNB Neural Engine — Modular Intelligence Framework 24×7
"""

import importlib, os, traceback
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

PLUGIN_DIR = "plugins"
ACTIVE_PLUGINS = {}
ADMIN_IDS = [123456789]  # Replace with your Telegram ID
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Modular Intelligence Framework 24×7"


# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []

    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            try:
                module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")

                # 🔥 Dual compatibility — supports both register_handlers() and register()
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Active"
                elif hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Active"
                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No Handler Found"
                    print(f"[WENBNB Loader] {module_name}: No register() function detected.")

                loaded.append(module_name)

            except Exception as e:
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {e}"
                failed.append((module_name, str(e)))
                print(f"[WENBNB Loader Error] {module_name}: {e}")

    print(f"[WENBNB Neural Loader] ✅ Loaded Modules: {loaded}")
    if failed:
        print(f"[WENBNB Neural Loader] ❌ Failed Modules: {failed}")
    return loaded, failed


# === /modules STATUS ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can check module status.")
        return

    text = "🧩 <b>WENBNB Plugin Status</b>\n\n"
    for name, status in ACTIVE_PLUGINS.items():
        text += f"• <b>{name}</b>: {status}\n"
    text += f"\n{BRAND_TAG}"

    update.message.reply_text(text, parse_mode="HTML")


# === /reload ===
def reload_plugins(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can reload modules.")
        return

    from main import dp
    ACTIVE_PLUGINS.clear()
    text = "🔄 <b>Reloading all plugins...</b>\n"
    loaded, failed = load_all_plugins(dp)
    text += f"✅ Loaded: {len(loaded)} | ❌ Failed: {len(failed)}\n\n{BRAND_TAG}"

    update.message.reply_text(text, parse_mode="HTML")


# === ERROR LOGGING ===
def plugin_error_handler(update, context):
    try:
        raise context.error
    except Exception as e:
        error_trace = "".join(traceback.format_exception(None, e, e.__traceback__))
        print(f"[Plugin Error] {error_trace}")
        if update and update.effective_user:
            update.message.reply_text(
                f"⚠️ Neural Core Error:\n<code>{str(e)}</code>", parse_mode="HTML"
            )


# === Register Core Commands ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    dp.add_error_handler(plugin_error_handler)
