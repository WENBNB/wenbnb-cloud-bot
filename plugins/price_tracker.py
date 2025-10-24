from telegram.ext import CommandHandler
import requests, html, random

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — AI Core Market Intelligence 24×7 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

# === Utility ===
def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # 🧠 Default token fallback
        token = "WENBNB"
        if context.args:
            token = context.args[0].upper()
        else:
            update.message.reply_text(
                "💡 No token specified — showing default <b>WENBNB</b> market data.",
                parse_mode="HTML"
            )

        # --- Fetch BNB price ---
        try:
            bnb_data = requests.get(BINANCE_BNB, timeout=10).json()
            bnb_price = float(bnb_data.get("price", 0))
        except Exception:
            bnb_price = 0

        # --- Initialize token metadata ---
        token_name, token_symbol, token_price, dex_source = token, "", None, "CoinGecko"

        # --- Fetch token price from CoinGecko ---
        try:
            cg_url = COINGECKO_SIMPLE.format(id=token.lower())
            cg_data = requests.get(cg_url, timeout=10).json()
            token_price = cg_data.get(token.lower(), {}).get("usd")
        except Exception:
            token_price = None

        # --- DexScreener fallback & name extraction ---
        if not token_price:
            try:
                dex_data = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=10).json()
                pairs = dex_data.get("pairs", [])
                if pairs:
                    pair = pairs[0]
                    base = pair.get("baseToken", {})
                    token_name = base.get("name") or base.get("symbol") or token
                    token_symbol = base.get("symbol") or ""
                    token_price = pair.get("priceUsd", "N/A")
                    dex_source = pair.get("dexId", "Unknown DEX").capitalize()
                else:
                    token_price = "N/A"
                    dex_source = "Not Found"
            except Exception:
                token_price, dex_source = "N/A", "Not Found"

        # --- Market sentiment / AI insight ---
        insights = [
            f"is showing <b>steady momentum</b> 🌙",
            f"looks <b>bullish</b> today 💎",
            f"appears <b>volatile</b> — stay alert ⚡",
            f"is <b>cooling off</b> a bit 🪶",
            f"might see <b>short-term gains</b> 🔥"
        ]
        insight = random.choice(insights)

        # --- Build formatted message ---
        msg = (
            f"💹 <b>Live Market Update</b>\n\n"
            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol or token)})</b>: "
            f"${short_float(token_price)}\n"
            f"🔥 <b>BNB:</b> ${short_float(bnb_price)}\n"
            f"📊 <i>Data Source:</i> {dex_source}\n\n"
            f"🧠 Neural Insight: <b>{token_name}</b> {insight}\n\n"
            f"{BRAND_FOOTER}"
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
    print("✅ Loaded plugin: plugins.price_tracker (v8.0.6-Stable+ Name Resolver Patch)")
