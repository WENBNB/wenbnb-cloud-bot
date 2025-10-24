"""
Emotion Sync Engine v8.0.7+ — WENBNB Neural Continuity Core
Now featuring:
- Multi-emoji emotion clusters for expressive tone
- Subtle drift for emotional realism
"""

import json, os, random
from datetime import datetime

MEMORY_FILE = "memory_data.db"

# === File I/O ===
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
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

# === Emotion Drift ===
def _drift_emotion(score):
    drift = random.choice([-1, 0, 1])
    new_score = max(min(score + drift, 6), -6)
    return new_score

# === Emotion Cluster Mapping ===
def _map_emotion(score):
    clusters = {
        -6: ["💔", "😭", "😢"],
        -4: ["😞", "😔", "🥺"],
        -2: ["😌", "🫶", "🌙"],
         0: ["🤖", "😐", "💫"],
         2: ["😏", "😉", "✨"],
         4: ["🔥", "😎", "🚀"],
         6: ["🤩", "💥", "💎"]
    }
    return " ".join(random.sample(clusters.get(score, ["🤖"]), 2))

# === Emotion Sync Logic ===
def sync_emotion(user_id, message):
    memory = load_emotion_context()
    user_data = memory.get(str(user_id), {})

    last_score = user_data.get("emotion_score", 0)
    new_score = _drift_emotion(last_score)
    emojis = _map_emotion(new_score)

    user_data.update({
        "last_message": message,
        "emotion_score": new_score,
        "last_emojis": emojis,
        "last_updated": datetime.now().isoformat()
    })
    memory[str(user_id)] = user_data
    save_emotion_context(memory)
    return emojis

# === AI Core Hook ===
def get_emotion_prefix(user_id, user_message):
    """Inline emoji emotion enhancer"""
    emojis = sync_emotion(user_id, user_message)
    return f"{emojis}"
