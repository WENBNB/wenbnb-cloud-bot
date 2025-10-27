# plugins/giveaway_ai.py
"""
WENBNB Smart Giveaway Manager v3.3-ProStable+ (EmotionClaim+ EmojiFix + ClearClaim Build)
────────────────────────────────────────────────────────────────────────────────────────
Features:
 • Multi-round auto giveaway (seconds-based)
 • Auto-winner selection per round
 • Winner DM + /claim_reward verification flow
 • Admin alert on claim + /claimed_list view
 • Admin command /clear_claims to reset claim records
 • Optional auto-clear when all winners claimed
 • Persistent JSON logs
 • Auto emoji + underscore fix
 • Premium emotionally adaptive UI
"""

import os
import json
import time
import random
import threading
import datetime
from typing import Dict, Any, List

from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext

# -----------------------
# Config / Files
# -----------------------
DATA_FILE = "giveaway_data.json"
CLAIMED_FILE = "claimed_rewards.json"
ADMIN_IDS = [5698007588]  # replace with your Telegram admin id(s)
BRAND_FOOTER = "⚡ <b>Powered by WENBNB Neural Engine</b> — Emotionally Aware. Always Active."

def _ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)

_ensure_file(DATA_FILE, {"active": False, "participants": [], "winners": [], "reward": "0 WENBNB"})
_ensure_file(CLAIMED_FILE, [])

# -----------------------
# Utility Helpers
# -----------------------
def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def bold(s: str) -> str:
    return f"<b>{s}</b>"

def get_reward_emoji(reward: str) -> str:
    r = (reward or "").upper()
    # order matters: check bigger tokens first
    if "USDT" in r:
        return "💰"
    if "BNB" in r and "WENBNB" not in r:
        return "🔶"
    if "ETH" in r:
        return "💎"
    if "WENBNB" in r:
        return "🌀"
    if "POINT" in r or "POINTS" in r:
        return "🎁"
    if "BTC" in r or "BITCOIN" in r:
        return "🪙"
    return "🏆"

# -----------------------
# Data Functions
# -----------------------
def load_data() -> Dict[str, Any]:
    return load_json(DATA_FILE)

def save_data(d: Dict[str, Any]):
    save_json(DATA_FILE, d)

def load_claimed() -> List[Dict[str, Any]]:
    return load_json(CLAIMED_FILE)

def save_claimed(lst: List[Dict[str, Any]]):
    save_json(CLAIMED_FILE, lst)

# -----------------------
# Giveaway Start
# -----------------------
def giveaway_start(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Only admins can start giveaways.")
        return

    args = context.args
    if len(args) < 3:
        update.message.reply_text("⚙️ Usage: /giveaway_start <reward> <rounds> <seconds>")
        return

    # convert underscores to spaces so display looks nice
    reward = args[0].replace("_", " ")
    emoji = get_reward_emoji(reward)

    try:
        rounds = int(args[1])
        seconds = int(args[2])
    except Exception:
        update.message.reply_text("⚠️ Rounds and seconds must be integers. Example: /giveaway_start 100_WENBNB 3 60")
        return

    data = {
        "active": True,
        "participants": [],
        "winners": [],
        "reward": reward,
        "round": 0,
        "total_rounds": rounds,
        "round_time": seconds,
        "started_at": datetime.datetime.utcnow().isoformat()
    }
    save_data(data)

    text = (
        f"💫 <b>WENBNB Multi-Round Giveaway Activated!</b>\n\n"
        f"🏆 Reward: {emoji} {bold(reward)}\n"
        f"🔄 Rounds: {rounds}\n"
        f"⏰ Round Duration: {seconds} seconds\n\n"
        f"🪩 <b>Join Now →</b> /join\n"
        f"Winners will be announced automatically after each round.\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")

    # start background thread for rounds (Render-safe)
    threading.Thread(target=_run_rounds_thread, args=(context.bot, update.effective_chat.id), daemon=True).start()

# -----------------------
# Join Giveaway
# -----------------------
def join_giveaway(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_data()

    if not data.get("active"):
        update.message.reply_text("⚠️ No active giveaway at the moment.")
        return

    participants = data.get("participants", [])
    if any(p.get("id") == user.id for p in participants):
        update.message.reply_text("✅ You’re already in this round!")
        return

    participants.append({"id": user.id, "username": user.username or user.first_name})
    data["participants"] = participants
    save_data(data)

    update.message.reply_text(f"🎯 @{user.username or user.first_name}, you’ve successfully joined the giveaway!\n\n{BRAND_FOOTER}", parse_mode="HTML")

# -----------------------
# Giveaway Info
# -----------------------
def giveaway_info(update: Update, context: CallbackContext):
    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No ongoing giveaway right now.")
        return

    text = (
        f"🎉 <b>Active Giveaway</b>\n"
        f"💰 Reward: {bold(data.get('reward'))}\n"
        f"🔁 Rounds: <b>{data.get('round')} / {data.get('total_rounds')}</b>\n"
        f"👥 Participants: <b>{len(data.get('participants', []))}</b>\n\n"
        f"🧠 Use /join to participate!\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# -----------------------
# Giveaway End (Admin)
# -----------------------
def giveaway_end(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Only admins can end giveaways.")
        return

    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No active giveaway to end.")
        return

    # set active false — background thread checks this frequently
    data["active"] = False
    save_data(data)
    update.message.reply_text("🧊 Giveaway force-ended by admin.", parse_mode="HTML")

    # If all winners already claimed, clear claim list to keep clean
    claimed = load_claimed()
    if claimed:
        # if every recorded claimed entry is marked claimed -> clear
        if all(c.get("claimed", False) for c in claimed):
            save_claimed([])
            try:
                context.bot.send_message(update.effective_chat.id, "🧾 All winners had already claimed — claim list auto-cleared ✅", parse_mode="HTML")
            except:
                pass

# -----------------------
# Wait helper (interruptible)
# -----------------------
def _wait_with_active_check(seconds: int) -> bool:
    """Sleep in 1s steps and return False early if giveaway was force-ended."""
    for _ in range(seconds):
        data = load_data()
        if not data.get("active"):
            return False
        time.sleep(1)
    return True

# -----------------------
# Round Logic (background)
# -----------------------
def _run_rounds_thread(bot: Bot, chat_id: int):
    # load fresh data each loop so admin updates are respected
    data = load_data()
    total = data.get("total_rounds", 1)
    reward = data.get("reward", "N/A")
    emoji = get_reward_emoji(reward)

    for current_round in range(1, total + 1):
        # reload and check active before starting
        data = load_data()
        if not data.get("active"):
            # giveaway was aborted
            try:
                bot.send_message(chat_id, "🛑 Giveaway stopped by admin. Cancelling remaining rounds.", parse_mode="HTML")
            except:
                pass
            break

        # update round number
        data["round"] = current_round
        save_data(data)

        round_time = data.get("round_time", 60)
        bot.send_message(chat_id, f"🔥 <b>Round {current_round} of {total} started!</b>\n💎 Reward: {emoji} {bold(reward)}\n💬 /join to enter now!\n⏳ Closing in {round_time} seconds...", parse_mode="HTML")

        # wait but allow admin to interrupt
        still_active = _wait_with_active_check(round_time)
        if not still_active:
            # admin killed giveaway during waiting
            try:
                bot.send_message(chat_id, "🛑 Giveaway stopped by admin during a round. Aborting.", parse_mode="HTML")
            except:
                pass
            break

        # reload participants and data
        data = load_data()
        # it might have been deactivated while we processed
        if not data.get("active"):
            try:
                bot.send_message(chat_id, "🛑 Giveaway was ended by admin. Stopping rounds.", parse_mode="HTML")
            except:
                pass
            break

        participants = data.get("participants", []) or []
        if participants:
            winner = random.choice(participants)
            winner_id = int(winner.get("id"))
            winner_username = winner.get("username") or str(winner_id)
            winner_entry = {
                "round": current_round,
                "id": winner_id,
                "username": winner_username,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "reward": reward,
                "claimed": False
            }

            # append to winners and clear participants
            data = load_data()
            winners = data.get("winners", [])
            winners.append(winner_entry)
            data["winners"] = winners
            data["participants"] = []
            save_data(data)

            # announce
            bot.send_message(chat_id, f"🏆 <b>Round {current_round} Winner:</b> @{winner_username}\n🎁 Reward: {emoji} {bold(reward)}\nWinner must DM /claim_reward.", parse_mode="HTML")

            # try to DM and register pending claim
            try:
                dm_text = (
                    f"🎉 Congratulations @{winner_username}! You were selected as the winner of Round {current_round}.\n\n"
                    f"🎁 Prize: {emoji} {bold(reward)}\n"
                    f"To claim, send /claim_reward in this chat.\n\n"
                    f"{BRAND_FOOTER}"
                )
                bot.send_message(chat_id=winner_id, text=dm_text, parse_mode="HTML")
                claimed = load_claimed()
                claimed.append({
                    "round": current_round,
                    "id": winner_id,
                    "username": winner_username,
                    "reward": reward,
                    "claimed": False,
                    "announced_at": datetime.datetime.utcnow().isoformat(),
                    "claimed_at": None
                })
                save_claimed(claimed)
            except Exception:
                bot.send_message(chat_id, f"⚠️ Could not DM @{winner_username}. They must DM the bot to claim.", parse_mode="HTML")
        else:
            bot.send_message(chat_id, f"😅 No participants in Round {current_round}.", parse_mode="HTML")

        # short break before next round (if any). Also allow admin kill during break.
        if current_round != total:
            bot.send_message(chat_id, "🕒 Next round begins in 10 seconds...", parse_mode="HTML")
            if not _wait_with_active_check(10):
                bot.send_message(chat_id, "🛑 Giveaway stopped by admin during inter-round break. Aborting.", parse_mode="HTML")
                break

    # finalize: set active false and publish summary
    data = load_data()
    data["active"] = False
    save_data(data)
    winners = ", ".join(f"@{w['username']}" for w in data.get("winners", [])) or "No winners"
    bot.send_message(chat_id, f"🏁 <b>Giveaway Complete!</b>\n\n💰 <b>Total Rounds:</b> {data.get('total_rounds', 0)}\n👑 <b>Winners:</b> {winners}\n\n{BRAND_FOOTER}", parse_mode="HTML")

    # auto-clear claims if every recorded claim is claimed
    claimed = load_claimed()
    if claimed and all(c.get("claimed", False) for c in claimed):
        save_claimed([])
        bot.send_message(chat_id, "🧾 All winners have claimed their rewards — claim list auto-cleared ✅", parse_mode="HTML")

# -----------------------
# Claim Reward (DM)
# -----------------------
def claim_reward(update: Update, context: CallbackContext):
    user = update.effective_user
    if update.effective_chat.type != "private":
        update.message.reply_text("⚠️ Please send /claim_reward in a private chat.")
        return

    claimed = load_claimed()
    pending = next((c for c in reversed(claimed) if c["id"] == user.id and not c["claimed"]), None)
    if not pending:
        update.message.reply_text("❌ No pending claim found.", parse_mode="HTML")
        return

    pending["claimed"] = True
    pending["claimed_at"] = datetime.datetime.utcnow().isoformat()
    save_claimed(claimed)

    data = load_data()
    for w in data.get("winners", []):
        if w["id"] == user.id and w["round"] == pending["round"]:
            w["claimed"] = True
    save_data(data)

    reward = pending.get("reward", "Reward")
    emoji = get_reward_emoji(reward)
    notify = (
        f"✅ <b>Giveaway Claim</b>\n"
        f"🎁 Reward: {emoji} {bold(reward)}\n"
        f"🏆 Winner: @{pending['username']} (ID: {pending['id']})\n"
        f"🔢 Round: {pending['round']}\n"
        f"🕒 Claimed at: {pending['claimed_at']}\n\n"
        f"{BRAND_FOOTER}"
    )
    for admin in ADMIN_IDS:
        try:
            context.bot.send_message(admin, notify, parse_mode="HTML")
        except:
            pass

    update.message.reply_text("🎉 Claim recorded! Admins have been notified.", parse_mode="HTML")

# -----------------------
# Claimed List (Admin)
# -----------------------
def claimed_list(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Admin only.")
        return

    claimed = load_claimed()
    if not claimed:
        update.message.reply_text("📭 No claims recorded yet.")
        return

    lines = ["📜 <b>Claimed / Pending Records</b>\n"]
    for c in claimed[-50:]:
        emoji = get_reward_emoji(c.get("reward", ""))
        status = "✅ Claimed" if c.get("claimed") else "⏳ Pending"
        claimed_at = c.get("claimed_at") or "—"
        lines.append(f"• R{c['round']} @{c['username']} — {emoji} {bold(c['reward'])} — {status} — Claimed at: {claimed_at}")

    lines.append(f"\n{BRAND_FOOTER}")
    update.message.reply_text("\n".join(lines), parse_mode="HTML")

# -----------------------
# Clear Claims (Admin)
# -----------------------
def clear_claims(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Only admins can clear claims.")
        return

    save_claimed([])
    update.message.reply_text("🧹 All claimed records cleared successfully.\n📁 claimed_rewards.json has been reset.", parse_mode="HTML")

# -----------------------
# Register Handlers
# -----------------------
def register_handlers(dp):
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dp.add_handler(CommandHandler("join", join_giveaway))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))
    dp.add_handler(CommandHandler("giveaway_info", giveaway_info))
    dp.add_handler(CommandHandler("claim_reward", claim_reward))
    dp.add_handler(CommandHandler("claimed_list", claimed_list))
    dp.add_handler(CommandHandler("clear_claims", clear_claims))
    print("✅ Loaded plugin: giveaway_ai.py v3.3-ProStable+ (EmotionClaim+ EmojiFix + ClearClaim Build)")
