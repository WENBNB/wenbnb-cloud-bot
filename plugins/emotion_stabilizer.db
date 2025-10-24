"""
Emotion Stabilizer v8.0.6 Beta — WENBNB Neural Engine
Balances long-term emotion drift from emotion_sync.py.
Auto-heals prolonged sadness or excessive excitement
to maintain a natural, realistic conversational tone.
"""

import json, os, random, time
from datetime import datetime, timedelta

MEMORY_FILE = "memory_data.db"

# === Helpers ===
def _load():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

# === Core stabilizer ===
def stabilize_emotion(user_id):
    """Smooth mood swings over time"""
    data = _load()
    u = data.get(str(user_id), {})
    score = u.get("emotion_score", 0)
    last = u.get("last_updated")

    # Apply soft recovery every 30 min
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

    u["emotion_score"] = max(min(score, 6), -6)
    u["last_updated"] = datetime.now().isoformat()

    # Update readable label
    mapping = {
        -6: "💔 deeply sad", -4: "😞 low", -2: "😌 calm",
         0: "🤖 neutral", 2: "😏 confident", 4: "🔥 energetic", 6: "🤩 euphoric"
    }
    u["emotion_label"] = mapping.get(u["emotion_score"], "🤖 balanced")

    data[str(user_id)] = u
    _save(data)
    return u["emotion_label"]

# === API for AI Core ===
def get_stabilized_emotion(user_id):
    """
    Called periodically (optional) from ai_auto_reply or emotion_sync
    to maintain long-term tone balance.
    """
    return stabilize_emotion(user_id)
