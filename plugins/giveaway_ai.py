# plugins/giveaway_ai.py
"""
WENBNB Smart Giveaway Manager
Version: 2.3 (Locked & Approved)
Mode: Hybrid (Command + AI Auto Task Tracking)
"""

import random, json, os, datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

DATA_FILE = "giveaway_data.json"
ADMIN_IDS = [5698007588]  # replace with your Telegram ID(s)
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"


# === UTILITIES ===

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"active": False, "participants": [], "reward": "0 WENBNB"}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(user_id):
    return user_id in ADMIN_IDS


# === CORE COMMANDS ===

def giveaway_start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Only admins can start a giveaway.")
        return

    args = context.args
    reward = args[0] if args else "100 WENBNB"
    data = {"active": True, "participants": [], "reward": reward}
    save_data(data)

    text = (
        f"🎉 <b>Giveaway Started!</b>\n\n"
        f"💎 Reward: <b>{reward}</b>\n"
        f"🧠 Join by sending /join\n\n"
        "Winners will be randomly selected when the event closes.\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def giveaway_end(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Only admins can end a giveaway.")
        return

    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No active giveaway to end.")
        return

    participants = data.get("participants", [])
    if not participants:
        update.message.reply_text("⚠️ No participants found.")
        data["active"] = False
        save_data(data)
        return

    winner = random.choice(participants)
    data["active"] = False
    save_data(data)

    text = (
        f"🏆 <b>Giveaway Ended!</b>\n"
        f"🎁 Reward: {data.get('reward')}\n"
        f"🎉 Winner: @{winner}\n\n"
        f"🕒 Ended on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def join_giveaway(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_data()

    if not data.get("active"):
        update.message.reply_text("⚠️ No active giveaway at the moment.")
        return

    if user.username in data["participants"]:
        update.message.reply_text("✅ You’re already in the giveaway!")
        return

    data["participants"].append(user.username)
    save_data(data)
    update.message.reply_text(f"🎯 @{user.username}, you’ve successfully joined the giveaway!\n\n{BRAND_FOOTER}")


def giveaway_info(update: Update, context: CallbackContext):
    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No ongoing giveaway right now.")
        return

    text = (
        f"🎉 <b>Active Giveaway</b>\n"
        f"💰 Reward: <b>{data.get('reward')}</b>\n"
        f"👥 Participants: <b>{len(data.get('participants', []))}</b>\n"
        f"🧠 Use /join to participate!\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")


# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))
    dp.add_handler(CommandHandler("join", join_giveaway))
    dp.add_handler(CommandHandler("giveaway_info", giveaway_info))

