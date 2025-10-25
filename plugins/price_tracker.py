"""
WENBNB Market Feed v8.4 — Smart Cascade + Fallback Edition
─────────────────────────────────────────────────────────────
• Multi-API Price Intelligence → Binance → CoinGecko → DexScreener
• Built-in WENBNB fallback with official launch message
• Auto-detected buy/chart links when data available
• Emotion-Synced Neural Message Style ⚡

💫 Powered by WENBNB Neural Engine — Market Intelligence Framework 24×7
"""

from telegram.ext import CommandHandler
import requests, html, random, math, os

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Intelligence v8.4 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_TICKER = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

# === CONFIG ===
DEFAULT_TOKEN = "WENBNB"
DEFAULT_WENBNB_CONTRACT = os.getenv("WEN_TOKEN_ADDRESS", "").strip()

# === Utility ===
def short_float(x):
    try:
        v = float(x)
        return f"{v:,.4f}" if v >= 1 else f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id: str) -> str:
    dex_id = (dex_id or "").lower()
    if "pancake" in dex_id: return "BSC"
    if "uniswap" in dex_id: return "Ethereum"
    if "base" in dex_id: return "Base"
    if "arbitrum" in dex_id: return "Arbitrum"
    if "solana" in dex_id: return "Solana"
    return "Unknown"

def neural_rank(liquidity_usd, volume24_usd):
    try:
        L, V = max(1, float(liquidity_usd)), max(1, float(volume24_usd))
        score = (math.log10(L)*0.6 + math.log10(V)*0.4)*10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except: return "N/A"

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        token = context.args[0].upper() if context.args else DEFAULT_TOKEN

        # --- Handle WENBNB fallback ---
        if token == "WENBNB" and not DEFAULT_WENBNB_CONTRACT:
            msg = (
                "💫 <b>WENBNB is evolving...</b>\n"
                "Official token feed coming online soon — stay tuned, Neural King 👑⚡\n\n"
                f"{BRAND_FOOTER}"
            )
            update.message.reply_text(msg, parse_mode="HTML")
            return

        # === Try Binance first ===
        token_price, dex_source, chain = None, "Binance", "BSC"
        try:
            if token in ["BNB", "BTC", "ETH", "SOL"]:
                pair = f"{token.upper()}USDT"
                res = requests.get(BINANCE_TICKER.format(symbol=pair), timeout=6).json()
                token_price = float(res.get("price", 0))
        except:
            token_price = None

        # === Fallback: CoinGecko ===
        if not token_price:
            try:
                cg_url = COINGECKO_SIMPLE.format(id=token.lower())
                cg = requests.get(cg_url, timeout=8).json()
                token_price = cg.get(token.lower(), {}).get("usd")
                dex_source = "CoinGecko"
            except:
                token_price = None

        # === Final fallback: DexScreener ===
        liquidity, volume24, nmr, chart_url = 0, 0, "N/A", None
        if not token_price:
            try:
                data = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=10).json()
                pairs = data.get("pairs", [])
                if pairs:
                    pair = pairs[0]
                    base = pair.get("baseToken", {})
                    token_price = pair.get("priceUsd", "N/A")
                    chain = detect_chain(pair.get("dexId"))
                    dex_source = pair.get("dexId", "DEX").capitalize()
                    liquidity = pair.get("liquidity", {}).get("usd", 0)
                    volume24 = pair.get("volume", {}).get("h24", 0)
                    nmr = neural_rank(liquidity, volume24)
                    chart_url = pair.get("url", None)
            except Exception as e:
                print("[DexScreener Error]", e)

        # === Compose final message ===
        insight = random.choice([
            f"<b>{token}</b> is gaining strong momentum 💎",
            f"<b>{token}</b> shows smart-money inflow 🧠",
            f"<b>{token}</b> trending with neural confidence ⚡",
            f"<b>{token}</b> volatility rising — traders alert 🔥"
        ])

        msg = (
            f"💹 <b>WENBNB Market Feed</b>\n\n"
            f"💎 <b>{html.escape(token)}</b>\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"📈 <i>Data Source:</i> {dex_source}\n\n"
            f"🧠 Insight: {insight}\n"
        )

        if chart_url:
            msg += f"\n🔗 <a href='{chart_url}'>View Chart / Buy</a>\n"

        msg += f"\n{BRAND_FOOTER}"
        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)

    except Exception as e:
        print("Error in /price:", e)
        update.message.reply_text(
            "⚙️ Neural Engine syncing... please retry soon.",
            parse_mode="HTML"
        )

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: price_tracker v8.4 Smart Cascade + Fallback Edition")
