"""
Emotion Sync Engine v8.0.6 — WENBNB Neural Continuity Core
Keeps emotional persistence across sessions and syncs with Stabilizer.
Smooth tone transitions and long-term emotional balance.
"""

import json, os, random
from datetime import datetime
from plugins.emotion_stabilizer import get_stabilized_emotion  # 🩶 Integration

MEMORY_FILE = "memory_data.db"

# === Load & Save ===
def load_emotion_context():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_emotion_context(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

# === Emotion Drift Algorithm ===
def _drift_emotion(score):
    """Soft drift to simulate emotional shifts"""
    drift = random.choice([-1, 0, 1])
    new_score = max(min(score + drift, 6), -6)
    return new_score

# === Emotion Tone Mapping ===
def _map_emotion(score):
    mapping = {
        -6: "💔 deeply sad",
        -4: "😞 low",
        -2: "😌 calm",
         0: "🤖 neutral",
         2: "😏 confident",
         4: "🔥 energetic",
         6: "🤩 euphoric"
    }
    return mapping.get(score, "🤖 balanced")

# === Sync Process ===
def sync_emotion(user_id, message):
    """Continuity layer: emotional persistence for each user"""
    memory = load_emotion_context()
    user_data = memory.get(str(user_id), {})

    last_score = user_data.get("emotion_score", 0)
    new_score = _drift_emotion(last_score)
    emotion = _map_emotion(new_score)

    # Update user emotional context
    user_data.update({
        "last_message": message,
        "emotion_score": new_score,
        "emotion_label": emotion,
        "last_updated": datetime.now().isoformat()
    })

    memory[str(user_id)] = user_data
    save_emotion_context(memory)
    return emotion

# === Exported for AI Core ===
def get_emotion_prefix(user_id, user_message):
    """Return real-time tone hint for the AI system prompt"""
    # Primary emotion from current chat
    emotion = sync_emotion(user_id, user_message)

    # Apply stabilizer soft correction
    stabilized_emotion = get_stabilized_emotion(user_id)
    emoji_only = stabilized_emotion.split(" ")[0] if stabilized_emotion else "🤖"

    # Combine dynamic tone context
    return f"🧠 Emotional continuity active — current mood synced: {emoji_only}."
