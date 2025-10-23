# plugins/admin_panel.py
"""
WENBNB Admin Command Manager + Analytics Dashboard v2.9
Locked & Approved — Neural Control System
"""

import os, json, time, datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Set your Telegram ID here
DATA_FILE = "admin_stats.json"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# === CORE DATA UTILITIES ===

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": 0, "messages": 0, "tokens_tracked": 0, "ai_queries": 0}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_event(event):
    data = load_data()
    data[event] = data.get(event, 0) + 1
    save_data(data)


# === ADMIN PANEL ===

def admin_panel(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != ADMIN_ID:
        update.message.reply_text("⚠️ You are not authorized to access the AI Command Center.")
        return

    data = load_data()
    text = (
        "<b>🤖 WENBNB Neural Admin Panel</b>\n\n"
        f"👥 Users: <b>{data['users']}</b>\n"
        f"💬 Messages: <b>{data['messages']}</b>\n"
        f"🧠 AI Queries: <b>{data['ai_queries']}</b>\n"
        f"💎 Tokens Tracked: <b>{data['tokens_tracked']}</b>\n"
        f"🕒 Uptime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{BRAND_FOOTER}"
    )

    keyboard = [
        [
            InlineKeyboardButton("📊 Refresh", callback_data="admin_refresh"),
            InlineKeyboardButton("🧹 Reset Stats", callback_data="admin_reset")
        ],
        [
            InlineKeyboardButton("🛠 Broadcast Message", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔐 Exit", callback_data="admin_exit")
        ]
    ]

    update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


def admin_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user = query.from_user

    if user.id != ADMIN_ID:
        query.answer("Unauthorized.", show_alert=True)
        return

    if data == "admin_refresh":
        query.answer("Refreshing...")
        admin_panel(update, context)
    elif data == "admin_reset":
        save_data({"users": 0, "messages": 0, "tokens_tracked": 0, "ai_queries": 0})
        query.edit_message_text("✅ Stats reset successfully!\n\n" + BRAND_FOOTER)
    elif data == "admin_broadcast":
        query.edit_message_text("🛠 Send me a message to broadcast to all users.\n(This feature is coming soon!)")
    elif data == "admin_exit":
        query.edit_message_text("🔒 Admin panel closed.\n\n" + BRAND_FOOTER)


# === USER ACTIVITY TRACKERS ===

def track_user_message(update: Update, context: CallbackContext):
    """Tracks total users & messages automatically."""
    user = update.effective_user
    data = load_data()

    data["messages"] += 1
    if "user_ids" not in data:
        data["user_ids"] = []
    if user.id not in data["user_ids"]:
        data["user_ids"].append(user.id)
        data["users"] = len(data["user_ids"])

    save_data(data)


def track_ai_query():
    data = load_data()
    data["ai_queries"] += 1
    save_data(data)


def track_token_usage():
    data = load_data()
    data["tokens_tracked"] += 1
    save_data(data)


# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(CallbackQueryHandler(admin_callback, pattern="admin_"))
