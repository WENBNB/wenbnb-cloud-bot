"""
WENBNB Emotion AI v8.4-Pro — Unified Emotion Engine
────────────────────────────────────────────────────────────
• Fusion of emotion_sync + emotion_stabilizer logic
• Maintains short-term vibe (emoji) + long-term tone (text)
• Self-healing drift across sessions via memory_data.db
• Generates mood prefix for AI Core and public chat feel
"""

import json, os, random
from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

SYNC_FILE = "emotion_sync.db"
STABILIZER_FILE = "emotion_stabilizer.db"
MAIN_MEMORY = "memory_data.db"

# === Low-Level Load/Save ===
def _load(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

# === Short-Term Drift ===
def _drift(score):
    return max(min(score + random.choice([-1, 0, 1]), 6), -6)

# === Tone Maps ===
def _emoji_cluster(score):
    clusters = {
        -6: ["💔", "😭", "😢"],
        -4: ["😞", "😔", "🥺"],
        -2: ["😌", "🫶", "🌙"],
         0: ["🤖", "😐", "💫"],
         2: ["😏", "😉", "✨"],
         4: ["🔥", "😎", "🚀"],
         6: ["🤩", "💥", "💎"]
    }
    return random.choice(clusters.get(score, ["🤖"]))

def _label(score):
    labels = {
        -6: "💔 deeply sad",
        -4: "😞 low",
        -2: "😌 calm",
         0: "🤖 neutral",
         2: "😏 confident",
         4: "🔥 energetic",
         6: "🤩 euphoric"
    }
    return labels.get(score, "🤖 balanced")

# === Unified Sync ===
def sync_emotion(user_id, message=""):
    """Update user emotion and store unified context."""
    sync_data = _load(SYNC_FILE)
    stab_data = _load(STABILIZER_FILE)
    memory = _load(MAIN_MEMORY)

    uid = str(user_id)
    entry = sync_data.get(uid, {})
    score = entry.get("emotion_score", 0)

    # drift update
    score = _drift(score)
    emoji = _emoji_cluster(score)
    label = _label(score)

    # stabilizer — slow recovery every 30min
    s_entry = stab_data.get(uid, {})
    last = s_entry.get("last_updated")
    if last:
        try:
            dt = datetime.fromisoformat(last)
            if datetime.now() - dt > timedelta(minutes=30):
                if score < 0:
                    score += 1
                elif score > 3:
                    score -= 1
        except Exception:
            pass
    s_entry["emotion_score"] = score
    s_entry["emotion_label"] = label
    s_entry["last_updated"] = datetime.now().isoformat()
    stab_data[uid] = s_entry

    # write all files
    sync_data[uid] = {
        "last_message": message,
        "emotion_score": score,
        "last_emojis": emoji,
        "last_updated": datetime.now().isoformat()
    }
    memory[uid] = {
        "last_message": message,
        "last_emotion": label,
        "last_emoji": emoji
    }

    _save(SYNC_FILE, sync_data)
    _save(STABILIZER_FILE, stab_data)
    _save(MAIN_MEMORY, memory)

    return emoji, label

# === Export for AI Core ===
def get_emotion_prefix(user_id, message):
    """Return fused emoji + tone hint for AI personality."""
    try:
        emoji, label = sync_emotion(user_id, message)
        vibe_line = random.choice([
            f"{emoji} Mood aligned → {label}",
            f"{emoji} Neural tone stabilized as {label}",
            f"{emoji} Emotional sync active: {label}",
            f"{emoji} WENBNB vibe check → {label}"
        ])
        return vibe_line
    except Exception:
        return "🤖 emotional link stable."


# ============================================================
# ✅ Plugin Registration Entry Point
# ============================================================

def emotionai_test(update: Update, context: CallbackContext):
    """Quick test to validate Emotion AI engine."""
    emoji, label = sync_emotion(update.effective_user.id, update.message.text)
    update.message.reply_text(f"🧠 Emotion AI synced: {emoji} → {label}")

def register(dispatcher):
    dispatcher.add_handler(CommandHandler("emotionai", emotionai_test))
    print("🧠 Emotion AI Engine v8.4-Pro registered successfully.")
