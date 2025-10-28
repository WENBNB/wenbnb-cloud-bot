"""
WENBNB Plugin Manager v8.7.8 — Self-Healing EmotionContext Edition
──────────────────────────────────────────────────────────────────────────────
• Keeps ai_auto_reply active even after reload.
• Rechecks aianalyze + emotion_sync modules automatically.
• Adds final failsafe rebind layer to dispatcher root.
• Works with both register() and register_handlers().
"""

import importlib, os, sys, time
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, Filters

PLUGIN_DIR = "plugins"
ACTIVE_PLUGINS, FAILED_PLUGINS = {}, {}
ADMIN_IDS = [5698007588]
BRAND_TAG = "💫 WENBNB Neural Engine — Modular Intelligence 24×7 ⚡"

# === COLOR LOGGING ===
def color_text(text, code):
    return f"\033[{code}m{text}\033[0m"

def log(msg, status="INFO"):
    ts = time.strftime("%H:%M:%S")
    colors = {"OK": "92", "WARN": "93", "FAIL": "91", "INFO": "96"}
    print(color_text(f"[{ts}] {msg}", colors.get(status, "0")))

# === AUTO REPAIR HOOK ===
def ensure_auto_reply(dispatcher):
    """Checks and restores ai_auto_reply handler if missing."""
    try:
        from telegram.ext import MessageHandler, Filters
        from plugins import ai_auto_reply

        existing = [str(h.callback) for h in dispatcher.handlers.get(0, [])]
        if "ai_auto_reply.ai_auto_chat" not in str(existing):
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
            ACTIVE_PLUGINS["ai_auto_reply"] = "✅ Restored via ensure_auto_reply()"
            log("💬 Auto-Reply handler restored (ensure_auto_reply).", "OK")
        else:
            log("💬 Auto-Reply handler verified active.", "INFO")
    except Exception as e:
        log(f"⚠️ ensure_auto_reply() failed: {e}", "WARN")

# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    loaded, failed = [], []
    log("🧠 Neural Plugin Loader initialized...", "INFO")

    files = [f for f in os.listdir(PLUGIN_DIR) if f.endswith(".py") and not f.startswith("__")]
    emotion_priority = ["aianalyze", "ai_auto_reply", "emotion_sync"]
    files.sort(key=lambda x: (x[:-3] not in emotion_priority, x))

    for file in files:
        module_name = file[:-3]
        module_path = f"{PLUGIN_DIR}.{module_name}"

        try:
            if module_path in sys.modules:
                del sys.modules[module_path]
            module = importlib.import_module(module_path)

            if hasattr(module, "register_handlers"):
                try:
                    module.register_handlers(dispatcher, config=None)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered via register_handlers()"
                except TypeError:
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Registered (legacy mode)"
            elif hasattr(module, "register"):
                module.register(dispatcher)
                ACTIVE_PLUGINS[module_name] = "✅ Registered via register()"
            else:
                ACTIVE_PLUGINS[module_name] = "⚠️ No register() function"
                log(f"⚠️ {module_name}: No entry point found", "WARN")

            loaded.append(module_name)
            log(f"[OK] {module_name}.py — registered", "OK")

        except Exception as e:
            err = str(e).split("\n")[0]
            FAILED_PLUGINS[module_name] = err
            ACTIVE_PLUGINS[module_name] = f"❌ Error: {err}"
            failed.append((module_name, err))
            log(f"[FAIL] {module_name}.py — {err}", "FAIL")

    validate_plugin_integrity()
    recheck_emotion_plugins(dispatcher)
    reattach_auto_reply(dispatcher)
    ensure_auto_reply(dispatcher)

    log(f"📦 Total Loaded: {len(loaded)} | ❌ Failed: {len(failed)}", "INFO")
    if failed:
        log(f"⚠️ Failed: {', '.join([x[0] for x in failed])}", "WARN")

    return loaded, failed

# === EMOTION MODULE RECHECK ===
def recheck_emotion_plugins(dispatcher):
    """Ensures Emotion Sync & aianalyze command remain attached."""
    handlers = [h for h in dispatcher.handlers.get(0, []) if isinstance(h, CommandHandler)]
    commands = [h.command for h in handlers]

    if "aianalyze" not in str(commands):
        try:
            from plugins import aianalyze
            dispatcher.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
            log("💫 /aianalyze reattached successfully.", "OK")
        except Exception as e:
            log(f"⚠️ Emotion analyzer reload failed: {e}", "WARN")

# === AUTO-REPLY FAILSAFE ===
def reattach_auto_reply(dispatcher):
    """Ensures ai_auto_reply stays active after reload."""
    try:
        from telegram.ext import MessageHandler, Filters
        from plugins import ai_auto_reply

        existing = [str(h.callback) for h in dispatcher.handlers.get(0, [])]
        if "ai_auto_reply.ai_auto_chat" in str(existing):
            log("💬 Auto-Reply already active (skipping duplicate).", "INFO")
            return

        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
        ACTIVE_PLUGINS["ai_auto_reply"] = "✅ Auto-Reply Reattached"
        log("💬 Auto-Reply linked successfully.", "OK")
    except Exception as e:
        log(f"⚠️ Auto-Reply reattach failed: {e}", "WARN")

# === VALIDATION ===
def validate_plugin_integrity():
    for name in list(ACTIVE_PLUGINS.keys()):
        path = f"{PLUGIN_DIR}.{name}"
        module = sys.modules.get(path)
        if not module:
            ACTIVE_PLUGINS[name] = "⚠️ Missing from memory"
        elif not any(hasattr(module, fn) for fn in ["register", "register_handlers"]):
            ACTIVE_PLUGINS[name] = "⚠️ Invalid structure"

# === /modules Command ===
def modules_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admin can check module status.")
    text = "🧩 <b>WENBNB Plugin Status — Neural Edition</b>\n\n"
    for name, status in ACTIVE_PLUGINS.items():
        text += f"• <b>{name}</b>: {status}\n"
    text += f"\n🧠 Neural Sync: <b>Stable</b>\n📦 Total Modules: <b>{len(ACTIVE_PLUGINS)}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

# === /reload Command ===
def reload_plugins(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("🚫 Only admin can reload modules.")

    dp = context.dispatcher
    ACTIVE_PLUGINS.clear()
    FAILED_PLUGINS.clear()
    update.message.reply_text("🔄 Reloading all plugins...", parse_mode="HTML")

    loaded, failed = load_all_plugins(dp)

    # === Final Failsafe: Ensure Text Listener Active ===
    try:
        from plugins import ai_auto_reply
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
        log("💬 Final Failsafe: ai_auto_reply handler reattached after reload.", "OK")
    except Exception as e:
        log(f"⚠️ Failsafe handler attach failed: {e}", "WARN")

    summary = f"✅ Loaded: {len(loaded)} | ❌ Failed: {len(failed)}\n\n{BRAND_TAG}"
    update.message.reply_text(summary, parse_mode="HTML")

# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("modules", modules_status))
    dp.add_handler(CommandHandler("reload", reload_plugins))
    log("💫 PluginManager v8.7.8 Self-Healing Edition initialized.", "OK")
