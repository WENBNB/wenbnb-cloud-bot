"""
🎯 WENBNB Airdrop Intelligence v4.2 — Alert Mode
Scans selected tokens at intervals and alerts admin when
simulated airdrop probability crosses the threshold.
🔥 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.2 💫
"""

import os
import math
import random
import time
import requests
from telegram.ext import CommandHandler, JobQueue, CallbackContext
from telegram import Update

# === CONFIG ===
DEX_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # set your Telegram ID in .env
ALERT_INTERVAL_MINUTES = 10                 # frequency of checks
ALERT_THRESHOLD = 70                        # % probability threshold
BRAND_TAG = "🎯 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.2 💫"

# Example tokens to monitor (add yours here)
WATCHLIST = {
    "BULLS": "0x78525f54e46d2821ec59bfae27201058881b4444",
    "TOKENFI": "0x1111111111111111111111111111111111111111",
    "WENBNB": "0x2222222222222222222222222222222222222222"
}

# Memory cache to prevent repeat alerts
LAST_ALERT = {}


# === Probability model (same as v4.1) ===
def estimate_airdrop_probability(liquidity_usd, volume24_usd):
    L = max(1.0, float(liquidity_usd))
    V = max(1.0, float(volume24_usd))
    l_score = math.log10(L)
    v_score = math.log10(V)
    raw = (l_score * 0.6 + v_score * 0.35)
    prob = max(0, min((raw / 6.0) * 100, 100))
    ratio = V / L
    if ratio > 0.05:
        prob += min((ratio * 100) * 0.3, 15)
    return max(0, min(prob, 100))


# === Core scanner ===
def scan_token(token_name, contract):
    try:
        r = requests.get(DEX_SEARCH.format(q=contract), timeout=10)
        data = r.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return None
        p = pairs[0]
        liquidity = p.get("liquidity", {}).get("usd", 0)
        volume24 = p.get("volume", {}).get("h24", 0)
        dex = p.get("dexId", "DEX").capitalize()
        price = p.get("priceUsd", "N/A")
        prob = estimate_airdrop_probability(liquidity, volume24)
        return {
            "name": token_name,
            "dex": dex,
            "liquidity": liquidity,
            "volume": volume24,
            "price": price,
            "prob": prob
        }
    except Exception:
        return None


# === Job loop ===
def job_scan_tokens(context: CallbackContext):
    bot = context.bot
    for name, addr in WATCHLIST.items():
        info = scan_token(name, addr)
        if not info:
            continue
        prob = info["prob"]
        # check threshold
        if prob >= ALERT_THRESHOLD:
            last_prob = LAST_ALERT.get(name, 0)
            # avoid spam if same token still above threshold with <10% change
            if abs(prob - last_prob) < 10:
                continue
            LAST_ALERT[name] = prob
            msg = (
                f"🚨 <b>Airdrop Alert</b>\n"
                f"💠 {name} — <i>{info['dex']}</i>\n"
                f"💰 Price: ${info['price']}\n"
                f"💧 Liquidity: ${info['liquidity']:,.2f}\n"
                f"📊 24h Volume: ${info['volume']:,.2f}\n"
                f"🎯 Airdrop Probability: <b>{prob:.0f}%</b>\n"
                f"🧠 Neural Insight: Activity spike detected — monitor project.\n\n"
                f"{BRAND_TAG}"
            )
            try:
                if ADMIN_ID:
                    bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="HTML")
            except Exception as e:
                print(f"[AlertSendError] {e}")


# === Manual command ===
def airdropalert_cmd(update: Update, context: CallbackContext):
    text = (
        "🧠 <b>WENBNB Airdrop Alert Mode</b>\n"
        f"Watching {len(WATCHLIST)} tokens.\n"
        f"Threshold: {ALERT_THRESHOLD}% | Interval: {ALERT_INTERVAL_MINUTES} min\n"
        "Next scan will trigger automatic admin alerts.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


# === Register ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropalert", airdropalert_cmd))
    # set up recurring job if job_queue available
    if hasattr(dispatcher, "job_queue") and isinstance(dispatcher.job_queue, JobQueue):
        job_queue: JobQueue = dispatcher.job_queue
        job_queue.run_repeating(job_scan_tokens, interval=ALERT_INTERVAL_MINUTES * 60, first=10)
        print(f"🎯 Airdrop Alert Mode active — scanning every {ALERT_INTERVAL_MINUTES} min.")
    else:
        print("⚠️ JobQueue not found; Alert Mode requires job_queue from main bot.")
    print("🎯 Loaded plugin: airdrop_alert.py (Alert Mode v4.2)")
