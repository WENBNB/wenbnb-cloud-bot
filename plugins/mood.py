"""
WENBNB Mood Command v8.4-Pro+ — Neural Emotion Visualizer
───────────────────────────────────────────────────────────────
Purpose:
- Displays current AI emotional state using emoji bars
- Combines data from emotion_sync + emotion_stabilizer
- Adds expressive UX layer (Pro+ visualization)
"""

import json, os, random
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from plugins.emotion_sync import get_emotion_prefix
from plugins.emotion_stabilizer import get_stabilized_emotion

SYNC_FILE = "emotion_sync.db"
STABILIZER_FILE = "emotion_stabilizer.db"

# === Helpers ===
def _load(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _mood_bar(score):
    """Generate visual emoji bar from -6 → +6"""
    levels = {
        -6: "💔💔💔🤍🤍🤍",
        -4: "😞😞🤍🤍🤍🤍",
        -2: "😌🤍🤍🤍🤍🤍",
         0: "🤖🤍🤍🤍🤍🤍",
         2: "😏✨🤍🤍🤍🤍",
         4: "🔥🔥⚡🤍🤍🤍",
         6: "🤩💎💫⚡🔥🚀"
    }
    return levels.get(score, "🤖🤍🤍🤍🤍🤍")

def mood_cmd(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)
    sync_data = _load(SYNC_FILE).get(user_id, {})
    stab_data = _load(STABILIZER_FILE).get(user_id, {})

    # Extract data
    drift_label = stab_data.get("emotion_label", "🤖 balanced")
    score = sync_data.get("emotion_score", 0)
    last_emoji = sync_data.get("last_emojis", "💫🤍")
    last_time = stab_data.get("last_updated", datetime.now().isoformat())

    # Visual elements
    bar = _mood_bar(score)
    tone_quote = random.choice([
        "💫 Neural calm achieved.",
        "⚡ Emotional systems stabilized.",
        "🔥 Circuits buzzing with life.",
        "🌙 Serenity mode engaged.",
        "💎 Energy frequency balanced.",
        "🚀 Mood resonance optimal."
    ])

    msg = (
        f"{last_emoji} <b>WENBNB Neural Mood Snapshot</b>\n"
        f"{bar}\n\n"
        f"• Current tone: <b>{drift_label}</b>\n"
        f"• Neural drift: <b>{score}</b>\n"
        f"• Status: {tone_quote}\n"
        f"• Last sync: <code>{last_time.split('T')[0]} {last_time.split('T')[1][:5]}</code>\n\n"
        f"💫 <i>Emotion Engine Synced — WENBNB v8.4-Pro+</i>"
    )

    update.message.reply_text(msg, parse_mode="HTML")

def register_handlers(dp):
    dp.add_handler(CommandHandler("mood", mood_cmd))
