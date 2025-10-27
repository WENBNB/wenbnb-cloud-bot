# plugins/giveaway_ai.py
"""
WENBNB Smart Giveaway Manager v3.1-ProStable+ (EmotionClaim Build)
────────────────────────────────────────────────────────────────
Features:
 - Multi-round auto giveaway (seconds-based)
 - Auto-winner selection per round
 - Winner DM + /claim_reward verification flow
 - Admin alert on claim + /claimed_list admin view
 - Persistent JSON logs: giveaway_data.json & claimed_rewards.json
 - Premium UI: bold reward, emoji, Render-safe background threads
 - Admin-only controls for start/end/add/remove
"""

import os
import json
import time
import random
import threading
import datetime
from typing import Dict, Any, List, Optional

from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext

# -----------------------
# Config / Files
# -----------------------
DATA_FILE = "giveaway_data.json"
CLAIMED_FILE = "claimed_rewards.json"
ADMIN_IDS = [5698007588]  # replace with your Telegram admin id(s)
BRAND_FOOTER = "⚡ <b>Powered by WENBNB Neural Engine</b> — Emotionally Aware. Always Active."

# ensure files exist
def _ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)

_ensure_file(DATA_FILE, {"active": False, "participants": [], "winners": [], "reward": "0 WENBNB"})
_ensure_file(CLAIMED_FILE, [])

# -----------------------
# Utilities
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

# -----------------------
# Data helpers
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
# Core Commands
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

    reward = args[0]
    try:
        rounds = int(args[1])
        seconds = int(args[2])
    except Exception:
        update.message.reply_text("⚠️ Rounds and seconds must be integers. Example: /giveaway_start 100_WENBNB 3 60")
        return

    data = {
        "active": True,
        "participants": [],   # list of {"id": int, "username": str}
        "winners": [],        # list of {"round": int, "id": int, "username": str, "timestamp": iso}
        "reward": reward,
        "round": 1,
        "total_rounds": rounds,
        "round_time": seconds,
        "started_at": datetime.datetime.utcnow().isoformat()
    }
    save_data(data)

    text = (
        f"💫 <b>WENBNB Multi-Round Giveaway Activated!</b>\n\n"
        f"🎁 Reward: {bold(reward)}\n"
        f"🔄 Rounds: {rounds}\n"
        f"⏰ Round Duration: {seconds} seconds\n\n"
        f"🪩 <b>Join Now →</b> /join\n"
        f"Winners will be announced automatically after each round.\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")

    # start background thread for rounds (Render-safe)
    threading.Thread(target=_run_rounds_thread, args=(context.bot, update.effective_chat.id), daemon=True).start()

def join_giveaway(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_data()

    if not data.get("active"):
        update.message.reply_text("⚠️ No active giveaway at the moment.")
        return

    # store both id and username for reliable DM
    participants: List[Dict[str, Any]] = data.get("participants", [])
    # check if already joined
    if any(p.get("id") == user.id for p in participants):
        update.message.reply_text("✅ You’re already in this round!")
        return

    participants.append({"id": user.id, "username": user.username or user.first_name})
    data["participants"] = participants
    save_data(data)

    update.message.reply_text(f"🎯 @{user.username or user.first_name}, you’ve successfully joined the giveaway!\n\n{BRAND_FOOTER}", parse_mode="HTML")

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

def giveaway_end(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Only admins can end giveaways.")
        return

    data = load_data()
    if not data.get("active"):
        update.message.reply_text("❌ No active giveaway to end.")
        return

    data["active"] = False
    save_data(data)
    update.message.reply_text("🧊 Giveaway force-ended by admin.", parse_mode="HTML")

# -----------------------
# Background rounds + winner flow
# -----------------------
def _run_rounds_thread(bot: Bot, chat_id: int):
    """
    Runs rounds in background. For each round:
      - announce start
      - sleep round_time
      - pick a random participant (if any)
      - append winner to data.winners with round number
      - DM winner with claim instructions and keep a pending_claims entry
      - clear participants for next round
    """
    data = load_data()
    total = data.get("total_rounds", 1)
    reward = data.get("reward", "N/A")
    round_time = data.get("round_time", 60)

    for current_round in range(1, total + 1):
        # update round field
        data = load_data()
        data["round"] = current_round
        save_data(data)

        # announce start
        bot.send_message(chat_id, f"🔥 <b>Round {current_round} of {total} started!</b>\n💎 Reward: {bold(reward)}\n/join to enter now!\n⏰ Closing in {round_time} seconds...", parse_mode="HTML")
        time.sleep(round_time)

        data = load_data()
        participants = data.get("participants", []) or []
        if participants:
            winner = random.choice(participants)
            winner_id = int(winner.get("id"))
            winner_username = winner.get("username") or str(winner_id)

            # record winner
            winner_entry = {
                "round": current_round,
                "id": winner_id,
                "username": winner_username,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "reward": reward,
                "claimed": False
            }
            data = load_data()
            data_winners = data.get("winners", [])
            data_winners.append(winner_entry)
            data["winners"] = data_winners
            # reset participants for next round
            data["participants"] = []
            save_data(data)

            # announce publicly
            bot.send_message(chat_id, f"🏆 <b>Round {current_round} Winner:</b> @{winner_username}\n🎁 Reward: {bold(reward)}\n\nI have sent a DM — winner must use /claim_reward to verify.", parse_mode="HTML")

            # DM winner privately
            try:
                dm_text = (
                    f"🎉 Congratulations @{winner_username}! You were selected as the winner of Round {current_round}.\n\n"
                    f"🎁 Prize: {bold(reward)}\n"
                    f"To claim, please reply here with the command: /claim_reward\n"
                    f"This helps us verify you and record the claim for admin review.\n\n"
                    f"{BRAND_FOOTER}"
                )
                bot.send_message(chat_id=winner_id, text=dm_text, parse_mode="HTML")
                # register pending claim in claimed file with claimed=False
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
            except Exception as e:
                # can't DM (maybe user blocked bot), still announce publicly
                bot.send_message(chat_id, f"⚠️ Could not DM @{winner_username}. They must DM the bot to claim.", parse_mode="HTML")
        else:
            bot.send_message(chat_id, f"😅 No participants in Round {current_round}.", parse_mode="HTML")

        # short break before next round (if any)
        if current_round != total:
            bot.send_message(chat_id, "🕒 Next round begins in 10 seconds...", parse_mode="HTML")
            time.sleep(10)

    # finalize
    data = load_data()
    data["active"] = False
    save_data(data)

    winners = ", ".join(f"@{w['username']}" for w in data.get("winners", [])) or "No winners"
    summary = (
        f"🏁 <b>Giveaway Complete!</b>\n\n"
        f"💰 <b>Total Rounds:</b> {total}\n"
        f"👑 <b>Winners:</b> {winners}\n\n"
        f"{BRAND_FOOTER}"
    )
    bot.send_message(chat_id, summary, parse_mode="HTML")

# -----------------------
# Claim flow (users in private chat)
# -----------------------
def claim_reward(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Must be DM (private chat)
    if update.effective_chat.type != "private":
        update.message.reply_text("⚠️ Please send /claim_reward in a private chat with the bot.")
        return

    claimed = load_claimed()
    # find latest unclaimed entry for this user
    pending = None
    for entry in reversed(claimed):
        if entry.get("id") == user.id and not entry.get("claimed", False):
            pending = entry
            break

    if not pending:
        update.message.reply_text("❌ No pending claim found for your account. Are you sure you were announced as a winner?", parse_mode="HTML")
        return

    # mark claimed
    pending["claimed"] = True
    pending["claimed_at"] = datetime.datetime.utcnow().isoformat()
    save_claimed(claimed)

    # update main winners list (claimed flag)
    data = load_data()
    for w in data.get("winners", []):
        if w.get("id") == user.id and w.get("round") == pending.get("round"):
            w["claimed"] = True
    save_data(data)

    # notify admin(s)
    notify_text = (
        f"✅ <b>Giveaway Claim</b>\n"
        f"🎁 Reward: {bold(pending.get('reward'))}\n"
        f"🏆 Winner: @{pending.get('username')} (ID: {pending.get('id')})\n"
        f"🔢 Round: {pending.get('round')}\n"
        f"🕒 Claimed at: {pending.get('claimed_at')}\n\n"
        f"{BRAND_FOOTER}"
    )
    bot: Bot = context.bot
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, notify_text, parse_mode="HTML")
        except Exception:
            pass

    # confirm to user
    update.message.reply_text("🎉 Claim recorded! Admins have been notified. Thank you.", parse_mode="HTML")

# -----------------------
# Admin: view claimed list
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
        status = "✅ Claimed" if c.get("claimed") else "⏳ Pending"
        claimed_at = c.get("claimed_at") or "—"
        lines.append(f"• R{c.get('round')} @{c.get('username')} — {bold(c.get('reward'))} — {status} — Claimed at: {claimed_at}")

    lines.append(f"\n{BRAND_FOOTER}")
    update.message.reply_text("\n".join(lines), parse_mode="HTML")

# -----------------------
# Register handlers
# -----------------------
def register_handlers(dp):
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dp.add_handler(CommandHandler("join", join_giveaway))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))
    dp.add_handler(CommandHandler("giveaway_info", giveaway_info))
    dp.add_handler(CommandHandler("claim_reward", claim_reward))
    dp.add_handler(CommandHandler("claimed_list", claimed_list))
    print("✅ Loaded plugin: giveaway_ai.py v3.1-ProStable+ (EmotionClaim Build)")
