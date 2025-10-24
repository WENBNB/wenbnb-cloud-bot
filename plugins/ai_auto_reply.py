"""
Emotion Sync Engine v8.0.5 — WENBNB Neural Continuity Core
Optimized for seamless AI emotion flow without visible text lines.
Features:
- Silent emoji-based emotional continuity
- Natural emotional drift algorithm
- Persistent mood storage across sessions
"""

import json, os, random
from datetime import datetime

MEMORY_FILE = "memory_data.db"

# === Load & Save ===
def load_emotion_context():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_emotion_context(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# === Emotion Drift ===
def _drift_emotion(score):
    drift = random.choice([-1, 0, 1])
    new_score = max(min(score + drift, 6), -6)
    return new_score

# === Emotion Mapping ===
def _map_emotion(score):
    mapping = {
        -6: "😭",
        -5: "😢",
        -4: "😞",
        -3: "😔",
        -2: "😌",
        -1: "🤖",
         0: "😎",
         1: "😊",
         2: "🙂",
         3: "💫",
         4: "🔥",
         5: "🤩",
         6: "🚀"
    }
    return mapping.get(score, "🤖")

# === Sync Process ===
def sync_emotion(user_id, message):
    """Track emotional state per user silently."""
    memory = load_emotion_context()
    user_data = memory.get(str(user_id), {})

    last_score = user_data.get("emotion_score", 0)
    new_score = _drift_emotion(last_score)
    emotion = _map_emotion(new_score)

    user_data.update({
        "last_message": message,
        "emotion_score": new_score,
        "emotion_label": emotion,
        "last_updated": datetime.now().isoformat()
    })

    memory[str(user_id)] = user_data
    save_emotion_context(memory)
    return emotion

# === Public API for AI Core ===
def get_emotion_prefix(user_id, user_message):
    """
    Returns only an emoji signal for the AI Core to blend emotion naturally.
    No text output is shown to users.
    """
    emotion = sync_emotion(user_id, user_message)
    return f"{emotion}"
