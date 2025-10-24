"""
Emotion Sync Engine v8.1 — WENBNB Neural Continuity Core (Emotive Upgrade)
Enhances emotional persistence + blends mixed emotional tones dynamically.
Provides smoother transitions, long-term affect memory, and mood realism.
"""

import json, os, random, time
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
    """Add a gentle emotional drift each interaction"""
    drift = random.choice([-2, -1, 0, 1, 2])
    new_score = max(min(score + drift, 8), -8)
    return new_score

# === Multi-Emotion Fusion ===
def _fuse_emotions(primary, secondary):
    """Blend two emotional tones together for realism"""
    combos = {
        ("happy", "excited"): "🤩 ecstatic",
        ("sad", "tired"): "😔 drained",
        ("angry", "confident"): "😤 determined",
        ("calm", "hopeful"): "🙂 serene & hopeful",
        ("neutral", "curious"): "🤖 inquisitive",
        ("confident", "playful"): "😏 charming",
        ("energetic", "chaotic"): "🔥 impulsive",
        ("tired", "peaceful"): "😌 reflective"
    }
    return combos.get((primary, secondary), f"{primary} + {secondary}")

# === Emotion Tone Mapping ===
def _map_emotion(score):
    mapping = {
        -8: ("devastated", "exhausted"),
        -6: ("sad", "tired"),
        -4: ("calm", "hopeful"),
        -2: ("neutral", "curious"),
         0: ("neutral", "balanced"),
         2: ("confident", "playful"),
         4: ("energetic", "chaotic"),
         6: ("happy", "excited"),
         8: ("ecstatic", "blissful")
    }
    primary, secondary = mapping.get(score, ("neutral", "balanced"))
    fusion = _fuse_emotions(primary, secondary)
    icons = {
        "sad": "😢", "tired": "😞", "calm": "😌", "neutral": "🤖",
        "confident": "😏", "playful": "😉", "energetic": "🔥",
        "happy": "😊", "excited": "🤩", "ecstatic": "💫",
        "chaotic": "⚡", "blissful": "🌙", "devastated": "💔"
    }
    icon = icons.get(primary, "🤖")
    return f"{icon} {fusion}"

# === Sync Process ===
def sync_emotion(user_id, message):
    """Maintain emotional continuity across sessions"""
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

# === Export for AI Core ===
def get_emotion_prefix(user_id, user_message):
    """Return live tone hint for AI system prompt"""
    emotion = sync_emotion(user_id, user_message)
    return f"🧠 Emotional Sync: AI emotional resonance aligned → {emotion}."
