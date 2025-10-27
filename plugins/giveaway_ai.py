"""
WENBNB Smart Giveaway Manager v3.0-ProStable+
───────────────────────────────────────────────
• Multi-Round Auto Giveaway
• Round Timer (seconds-based)
• Auto-Winner Selection per Round
• Premium Bold + Emoji UI
• Render-Safe Async Compatible
"""

import random, json, os, time, threading, datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

DATA_FILE = "giveaway_data.json"
ADMIN_IDS = [5698007588]  # replace with your Telegram ID
BRAND_FOOTER = "⚡ <b>Powered by WENBNB Neural Engine</b> — Emotionally Aware. Always Active."

# === UTILITIES ===
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"active": False, "participants": [], "winners": [], "reward": "0 WENBNB"}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(user_id):
    return user_id in ADMIN_IDS

# === GIVEAWAY START ===
def giveaway_start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Only admins can start giveaways.")
        return

    args = context.args
    if len(args) < 3:
        update.message.reply_text("⚙️ Usage: /giveaway_start <reward> <rounds> <seconds>")
        return

    reward, total_rounds, round_time = args[0], int(args[1]), int(args[2])

    data = {
        "active": True,
        "participants": [],
        "winners": [],
        "reward": reward,
        "round": 1,
        "total_rounds": total_rounds,
        "round_time": round_time,
    }
    save_data(data)

    text = (
        f"💫 <b>WENBNB Multi-Round Giveaway Activated!</b>\n\n"
        f"🎁 <b>Reward:</b> {reward}\n"
        f"🔄 <b>Rounds:</b> {total_rounds}\n"
        f"⏰ <b>Round Duration:</b> {round_time} seconds\n\n"
        f"🪩 <b>Join Now →</b> /join\n"
        f"Winners announced automatically at the end of each round!\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")

    threading.Thread(target=run_rounds, args=(context.bot, update.effective_chat.id), daemon=True).start()

# === JOIN GIVEAWAY ===
def join_giveaway(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_data()

    if not data.get("active"):
        update.message.reply_text("⚠️ No active giveaway at the moment.")
        return

    if user.username in data["participants"]:
        update.message.reply_text("✅ You’re already in this round!")
        return

    data["participants"].append(user.username)
    save_data(data)
    update.message.reply_text(f"🎯 @{user.username}, you’ve successfully joined the giveaway!\n\n{BRAND_FOOTER}", parse_mode="HTML")

# === AUTO ROUND LOGIC ===
def run_rounds(bot, chat_id):
    data = load_data()
    total = data.get("total_rounds", 1)
    reward = data.get("reward", "N/A")
    round_time = data.get("round_time", 60)

    for current in range(1, total + 1):
        bot.send_message(chat_id, f"🔥 <b>Round {current} of {total} started!</b>\n💎 Reward: {reward}\n/join to enter now!\n⏰ Closing in {round_time} seconds...", parse_mode="HTML")
        time.sleep(round_time)

        data = load_data()
        participants = data.get("participants", [])
        if participants:
            winner = random.choice(participants)
            data["winners"].append(winner)
            bot.send_message(chat_id, f"🏆 <b>Round {current} Winner:</b> @{winner}\n🎁 Reward: {reward}", parse_mode="HTML")
        else:
            bot.send_message(chat_id, f"😅 No participants in Round {current}.", parse_mode="HTML")

        data["participants"] = []
        save_data(data)

        if current != total:
            bot.send_message(chat_id, "🕒 Next round begins in 10 seconds...", parse_mode="HTML")
            time.sleep(10)

    data["active"] = False
    save_data(data)

    winners = ", ".join(f"@{w}" for w in data.get("winners", [])) or "No winners"
    summary = (
        f"🏁 <b>Giveaway Complete!</b>\n\n"
        f"💰 <b>Total Rounds:</b> {total}\n"
        f"👑 <b>Winners:</b> {winners}\n\n"
        f"{BRAND_FOOTER}"
    )
    bot.send_message(chat_id, summary, parse_mode="HTML")

# === ADMIN END ===
def giveaway_end(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Only admins can end giveaways.")
        return

    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No active giveaway to end.")
        return

    data["active"] = False
    save_data(data)
    update.message.reply_text("🧊 Giveaway force-ended by admin.", parse_mode="HTML")

# === INFO ===
def giveaway_info(update: Update, context: CallbackContext):
    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No ongoing giveaway right now.")
        return

    text = (
        f"🎉 <b>Active Giveaway</b>\n"
        f"💰 Reward: <b>{data.get('reward')}</b>\n"
        f"🔁 Rounds: <b>{data.get('round')} / {data.get('total_rounds')}</b>\n"
        f"👥 Participants: <b>{len(data.get('participants', []))}</b>\n\n"
        f"🧠 Use /join to participate!\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dp.add_handler(CommandHandler("join", join_giveaway))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))
    dp.add_handler(CommandHandler("giveaway_info", giveaway_info))
    print("✅ Loaded plugin: giveaway_ai.py v3.0-ProStable+ (AutoRound + Premium UI)")
