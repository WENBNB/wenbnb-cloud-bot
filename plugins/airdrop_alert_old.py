"""
🎯 WENBNB Neural Sentinel v5.0 — Smart Airdrop Alert System
Hybrid monitoring of tokens using adaptive threshold, learning watchlist,
and behavioral delta tracking.
🔥 Powered by WENBNB Neural Engine — Airdrop Intelligence v5.0 ⚡
"""

import os
import math
import time
import random
import requests
from telegram.ext import CommandHandler, JobQueue, CallbackContext
from telegram import Update

# === CONFIG ===
DEX_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DEFAULT_INTERVAL = 10          # minutes
DEFAULT_THRESHOLD = 70         # %
BRAND_TAG = "🎯 Powered by WENBNB Neural Engine — Airdrop Intelligence v5.0 ⚡"

# Persistent runtime state
WATCHLIST = {
    "BULLS": "0x78525f54e46d2821ec59bfae27201058881b4444",
    "TOKENFI": "0x1111111111111111111111111111111111111111",
    "WENBNB": "0x2222222222222222222222222222222222222222"
}
LAST_ALERT = {}
LAST_LIQUIDITY = {}
SETTINGS = {"interval": DEFAULT_INTERVAL, "threshold": DEFAULT_THRESHOLD}


# === Probability model (adaptive) ===
def estimate_airdrop_probability(liquidity_usd, volume24_usd):
    L = max(1.0, float(liquidity_usd))
    V = max(1.0, float(volume24_usd))
    l_score = math.log10(L)
    v_score = math.log10(V)
    base = (l_score * 0.6 + v_score * 0.35)
    prob = max(0, min((base / 6.0) * 100, 100))
    ratio = V / L
    if ratio > 0.05:
        prob += min((ratio * 100) * 0.3, 15)
    return max(0, min(prob, 100))


def adaptive_threshold(liquidity):
    """Adjust alert sensitivity based on liquidity levels."""
    if liquidity < 50_000:
        return 55
    elif liquidity < 250_000:
        return 65
    elif liquidity < 1_000_000:
        return 75
    else:
        return 85


# === Dex fetch ===
def probe_token(name, address):
    try:
        r = requests.get(DEX_SEARCH.format(q=address), timeout=10)
        data = r.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return None
        p = pairs[0]
        liquidity = p.get("liquidity", {}).get("usd", 0)
        volume = p.get("volume", {}).get("h24", 0)
        dex = p.get("dexId", "DEX").capitalize()
        price = p.get("priceUsd", "N/A")
        prob = estimate_airdrop_probability(liquidity, volume)
        return {"name": name, "dex": dex, "liquidity": liquidity,
                "volume": volume, "price": price, "prob": prob}
    except Exception:
        return None


# === Main loop ===
def job_scan_tokens(context: CallbackContext):
    bot = context.bot
    threshold_base = SETTINGS["threshold"]

    for name, addr in WATCHLIST.items():
        info = probe_token(name, addr)
        if not info:
            continue

        liquidity = info["liquidity"]
        prob = info["prob"]

        # compute adaptive threshold
        th = max(threshold_base, adaptive_threshold(liquidity))

        # behavioral detection
        prev_liq = LAST_LIQUIDITY.get(name, liquidity)
        delta = ((liquidity - prev_liq) / prev_liq * 100) if prev_liq else 0
        LAST_LIQUIDITY[name] = liquidity

        insight = "Stable conditions observed."
        if delta > 20:
            insight = "🚀 Rapid liquidity inflow — possible campaign activity."
        elif delta < -20:
            insight = "📉 Liquidity drop — reduced activity or sell pressure."
        elif prob > th + 10:
            insight = "🔥 Momentum surge — increasing trading signals."

        # threshold logic
        if prob >= th:
            last_prob = LAST_ALERT.get(name, 0)
            if abs(prob - last_prob) < 8:
                continue
            LAST_ALERT[name] = prob

            msg = (
                f"🚨 <b>Neural Airdrop Alert</b>\n"
                f"💠 {name} — <i>{info['dex']}</i>\n"
                f"💰 Price: ${info['price']}\n"
                f"💧 Liquidity: ${info['liquidity']:,.2f} ({delta:+.1f}% Δ)\n"
                f"📊 24h Volume: ${info['volume']:,.2f}\n"
                f"🎯 Probability: <b>{prob:.0f}%</b> (Threshold {th}%)\n"
                f"🧠 Insight: {insight}\n\n"
                f"{BRAND_TAG}"
            )

            try:
                if ADMIN_ID:
                    bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="HTML")
            except Exception as e:
                print(f"[AlertSendError] {e}")


# === Commands ===
def airdropalert_cmd(update: Update, context: CallbackContext):
    text = (
        "🧠 <b>WENBNB Neural Airdrop Sentinel</b>\n"
        f"Watching {len(WATCHLIST)} tokens.\n"
        f"Interval: {SETTINGS['interval']} min | Threshold: {SETTINGS['threshold']}%\n"
        f"Adaptive sensitivity enabled.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def alertconfig_cmd(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        return update.message.reply_text(
            "⚙️ Usage: /alertconfig threshold=75 interval=5", parse_mode="HTML"
        )
    for arg in args:
        if arg.startswith("threshold="):
            SETTINGS["threshold"] = int(arg.split("=")[1])
        elif arg.startswith("interval="):
            SETTINGS["interval"] = int(arg.split("=")[1])
    update.message.reply_text(
        f"✅ Updated AlertConfig:\nThreshold: {SETTINGS['threshold']}%\n"
        f"Interval: {SETTINGS['interval']} min", parse_mode="HTML"
    )


# === Register ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropalert", airdropalert_cmd))
    dispatcher.add_handler(CommandHandler("alertconfig", alertconfig_cmd))

    if hasattr(dispatcher, "job_queue") and isinstance(dispatcher.job_queue, JobQueue):
        job_queue: JobQueue = dispatcher.job_queue
        job_queue.run_repeating(
            job_scan_tokens,
            interval=SETTINGS["interval"] * 60,
            first=10
        )
        print(f"🎯 Neural Sentinel active — scanning every {SETTINGS['interval']} min.")
    else:
        print("⚠️ JobQueue not found; Alert Mode requires job_queue.")
    print("🎯 Loaded plugin: airdrop_alert.py (Neural Sentinel v5.0)")
