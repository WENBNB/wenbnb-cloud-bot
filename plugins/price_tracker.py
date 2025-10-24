from telegram.ext import CommandHandler
import requests
import html

def price_cmd(update, context):
    try:
        # Typing indicator
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Determine token name
        token = "WENBNB"
        if context.args:
            token = context.args[0].upper()

        # --- Fetch BNB price ---
        bnb_data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT").json()
        bnb_price = float(bnb_data["price"])

        # --- Fetch token price from CoinGecko ---
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={token.lower()}&vs_currencies=usd"
        cg_data = requests.get(cg_url).json()
        token_price = cg_data.get(token.lower(), {}).get("usd", None)

        # --- Dexscreener fallback ---
        if not token_price:
            dex_data = requests.get(f"https://api.dexscreener.io/latest/dex/search?q={token}").json()
            pairs = dex_data.get("pairs", [])
            if pairs:
                token_price = pairs[0].get("priceUsd", "N/A")
                dex_source = pairs[0].get("dexId", "Unknown DEX").capitalize()
            else:
                token_price = "N/A"
                dex_source = "Not Found"
        else:
            dex_source = "CoinGecko"

        # --- Response formatting ---
        msg = (
            f"💹 <b>Live Market Update</b>\n\n"
            f"💎 <b>{html.escape(token)}</b>: ${token_price}\n"
            f"🔥 <b>BNB:</b> ${bnb_price:,.2f}\n"
            f"📊 <i>Data Source:</i> {dex_source}\n\n"
            f"🤖 Powered by <b>WENBNB Neural Engine</b> — AI Core Market Intelligence 24×7 ⚡"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text("⚠️ Error fetching price data. Please try again later.")

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker")
