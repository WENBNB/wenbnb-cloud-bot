"""
WENBNB Neural Engine — v5.6 Stable Edition
────────────────────────────────────────────
Restored legacy fallback behavior for /price and /price wenbnb.
Now prefers DexScreener > CoinGecko > Binance.
"""

from telegram.ext import CommandHandler
import requests, html, random, math, time

# === Branding ===
BRAND_FOOTER = "💫 Powered by WENBNB Neural Engine — AI Core Market Intelligence 24×7 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

# === Utils ===
def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id: str) -> str:
    dex_id = (dex_id or "").lower()
    if "pancake" in dex_id: return "BSC"
    if "uniswap" in dex_id: return "Ethereum"
    if "base" in dex_id: return "Base"
    if "arbitrum" in dex_id: return "Arbitrum"
    return "Unknown"

def neural_market_rank(L, V):
    try:
        L = max(1.0, float(L))
        V = max(1.0, float(V))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except Exception:
        return "N/A"

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # 🧠 Default Token Fallback
        token = context.args[0].upper() if context.args else "WENBNB"
        if not context.args:
            update.message.reply_text(
                "💡 No token specified — showing default <b>WENBNB</b> market data.",
                parse_mode="HTML"
            )

        # --- Fetch BNB price ---
        try:
            bnb_data = requests.get(BINANCE_BNB, timeout=8).json()
            bnb_price = float(bnb_data.get("price", 0))
        except:
            bnb_price = 0

        token_name, token_symbol, token_price, dex_source = token, token, "N/A", "Not Found"
        chain, liquidity, volume24, nmr = "Unknown", 0, 0, "N/A"

        # --- Step 1: DexScreener first (better accuracy for new tokens)
        try:
            dex_data = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=8).json()
            pairs = dex_data.get("pairs", [])
            if pairs:
                pair = pairs[0]
                base = pair.get("baseToken", {})
                token_name = base.get("name") or token
                token_symbol = base.get("symbol") or token
                token_price = pair.get("priceUsd", "N/A")
                dex_source = pair.get("dexId", "Unknown DEX").capitalize()
                chain = detect_chain(dex_source)
                liquidity = pair.get("liquidity", {}).get("usd", 0)
                volume24 = pair.get("volume", {}).get("h24", 0)
                nmr = neural_market_rank(liquidity, volume24)
        except:
            pass

        # --- Step 2: CoinGecko fallback only if Dex fails
        if token_price in ["N/A", None, 0]:
            try:
                cg_data = requests.get(COINGECKO_SIMPLE.format(id=token.lower()), timeout=8).json()
                cg_price = cg_data.get(token.lower(), {}).get("usd")
                if cg_price:
                    token_price = cg_price
                    dex_source = "CoinGecko"
                    chain = "Centralized"
                    nmr = "A+"
            except:
                pass

        # --- If still N/A ---
        if token_price in ["N/A", None, 0]:
            update.message.reply_text(
                f"❌ No valid market data for <b>{html.escape(token)}</b>.\n"
                f"Tip: Try using contract address or known Dex token name.",
                parse_mode="HTML"
            )
            return

        # --- Neural Insight ---
        insights = [
            f"is showing <b>steady momentum</b> 🌙",
            f"has <b>organic trading activity</b> 🌿",
            f"is <b>recovering volume</b> 💎",
            f"shows <b>AI-flagged smart money movement</b> ⚡",
            f"may see <b>short-term volatility</b> 🧠",
        ]
        insight = random.choice(insights)

        ts = time.strftime("%H:%M:%S", time.localtime())

        # --- Build final output ---
        msg = (
            f"💎 <b>Live Market Update</b>\n\n"
            f"💠 <b>{html.escape(token_name)}</b>\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"📈 <i>Data Source:</i> {dex_source}\n\n"
            f"🧠 Neural Insight: <b>{token_name}</b> {insight}\n\n"
            f"{BRAND_FOOTER}\n⏱️ {ts}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text(
            "⚙️ Neural Engine syncing... please retry soon.",
            parse_mode="HTML"
        )

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v5.6 Stable)")
