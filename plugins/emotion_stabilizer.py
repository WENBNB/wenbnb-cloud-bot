"""
Emotion Stabilizer v8.3-Pro — WENBNB Neural Engine
────────────────────────────────────────────────────────────
Purpose:
• Smooths long-term mood drift
• Balances energy from emotion_sync.py
• Adds text-based tone modulation (context-aware)
• Feeds stabilized label back to AI layer

File: emotion_stabilizer.db
"""

import json, os, re, random
from datetime import datetime, timedelta

MEMORY_FILE = "emotion_stabilizer.db"

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
    except Exception:
        pass


# === Core Text Tone Analyzer ===
def _text_tone_score(text):
    """
    Quick tone estimation based on message content.
    Returns an integer adjustment (-2 to +2)
    """

    text = text.lower()

    positive = ["great", "win", "moon", "love", "pumped", "bull", "happy", "🔥", "🚀"]
    negative = ["bad", "lose", "sad", "dump", "bear", "angry", "red", "😭"]
    calm = ["ok", "fine", "slow", "chill", "peace", "hodl", "neutral"]
    hype = ["meme", "crazy", "ai", "trend", "viral", "moon", "lit"]

    if any(w in text for w in positive):
        return +2
    elif any(w in text for w in negative):
        return -2
    elif any(w in text for w in hype):
        return +1
    elif any(w in text for w in calm):
        return 0
    else:
        return random.choice([-1, 0, 1])  # small natural jitter


# === Core Stabilizer ===
def stabilize_emotion(user_id, text=""):
    """
    Smooth mood swings and evolve tone over time.
    Integrates message tone + cooldown + drift control.
    """
    data = _load()
    u = data.get(str(user_id), {})
    score = u.get("emotion_score", 0)
    last = u.get("last_updated")

    # Apply cooldown drift every 30 min
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

    # Apply tone score modulation
    tone_adj = _text_tone_score(text)
    score += tone_adj
    score = max(min(score, 6), -6)

    # Label mapping (expanded for realism)
    mapping = {
        -6: "💔 deeply sad",
        -4: "😞 drained",
        -2: "😌 mellow",
         0: "🤖 neutral",
         2: "😏 confident",
         4: "🔥 energized",
         6: "🤩 euphoric"
    }

    label = mapping.get(score, "🤖 balanced")

    u.update({
        "emotion_score": score,
        "emotion_label": label,
        "last_updated": datetime.now().isoformat(),
        "last_input": text[:120] if text else ""
    })

    data[str(user_id)] = u
    _save(data)

    return label


# === Public API for AI Core ===
def get_stabilized_emotion(user_id, text=""):
    """
    Public accessor — returns stabilized emotion label for given user/message.
    """
    try:
        return stabilize_emotion(user_id, text)
    except Exception:
        return "🤖 neutral"
