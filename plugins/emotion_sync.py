"""
Emotion Sync Engine v8.3 — WENBNB Neural Continuity Core
────────────────────────────────────────────────────────────
Purpose:
• Tracks short-term emotional drift per user (memory persistence)
• Generates expressive emoji clusters (state sync)
• Classifies emotional sentiment + context labels
• Returns hashtags + mood cues for AI modules

Build: v8.3-Full (Pro Mode Ready)
"""

import json, os, random
from datetime import datetime

# === File Configuration ===
MEMORY_FILE = "emotion_sync.db"

# === File I/O ===
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
    except Exception:
        pass


# === Emotion Drift Logic ===
def _drift_emotion(score):
    """Random short-term drift between -6 and +6."""
    drift = random.choice([-1, 0, 1])
    return max(min(score + drift, 6), -6)


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


# === Emotion Sync Memory Core ===
def sync_emotion(user_id, message):
    """Stores and evolves user's emotional drift."""
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
    """Inline emoji emotion enhancer for quick use in AI replies."""
    try:
        return sync_emotion(user_id, user_message)
    except Exception:
        return "🤖"


# ============================================================
# 🌈 Emotion Label Engine — v8.3 Add-On
# ============================================================

def analyze_sentiment(text):
    """
    Lightweight sentiment + context labeler.
    Returns: dict -> { sentiment, tags, mood }
    """

    text_lower = text.lower()
    sentiment = "Neutral 😐"
    tags = "#StayBased #CryptoFeels"

    # Keyword sentiment map (expandable in future versions)
    bullish_words = ["moon", "pump", "up", "gain", "win", "green", "bull", "profit", "surge"]
    bearish_words = ["down", "dump", "red", "lose", "loss", "pain", "bear", "crash"]
    hype_words = ["ai", "meme", "trend", "viral", "crazy", "lit", "energy", "pump it"]
    calm_words = ["chill", "relax", "peace", "hodl", "slow", "steady", "patience"]

    if any(w in text_lower for w in bullish_words):
        sentiment = "Bullish 🟢"
        tags = "#BullVibes #HODL #CryptoLife"
    elif any(w in text_lower for w in bearish_words):
        sentiment = "Bearish 🔴"
        tags = "#BearMood #MarketFeels #StayStrong"
    elif any(w in text_lower for w in hype_words):
        sentiment = "Hyped 💥"
        tags = "#AIEnergy #MemeDrop #CryptoBuzz"
    elif any(w in text_lower for w in calm_words):
        sentiment = "Calm 🌙"
        tags = "#ZenMode #StayBased #CryptoPeace"

    # Random emotional twist (to keep replies fresh)
    mood_emojis = random.choice(["😎", "🤓", "🥱", "🤔", "💫", "😏", "🫡", "🔥"])

    return {
        "sentiment": sentiment,
        "tags": tags,
        "mood": mood_emojis
    }
