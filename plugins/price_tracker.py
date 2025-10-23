import requests
from telegram import Update
from telegram.ext import CallbackContext
import html

def register(dp):
    dp.add_handler(CommandHandler("price", price_command))

def price_command(update: Update, context: CallbackContext):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Determine token name
        token = "WENBNB"
        if context.args:
            token = context.args[0].upper()

        bnb_data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT").json()
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={token.lower()},binancecoin&vs_currencies=usd"
        cg_data = requests.get(cg_url).json()

        bnb_price = float(bnb_data["price"])
        token_price = cg_data.get(token.lower(), {}).get("usd", None)

        if not token_price:
            # Fallback to DexScreener if token not found on CoinGecko
            dex_data = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={token}").json()
            pairs = dex_data.get("pairs", [])
            if pairs:
                token_price = pairs[0].get("priceUsd", "N/A")
                dex_source = pairs[0].get("dexId", "Unknown DEX")
            else:
                token_price = "N/A"
                dex_source = "Not Found"

        else:
            dex_source = "CoinGecko"

        text = (
            f"📊 <b>Live Market Update</b>\n\n"
            f"💰 <b>BNB:</b> ${bnb_price:,.2f} (Binance)\n"
            f"💎 <b>{html.escape(token)}:</b> ${token_price} ({dex_source})\n\n"
            f"⚡ Data auto-updated via live feed\n"
            f"🚀 <b>Powered by WENBNB Neural Engine — AI Core Intelligence 24×7</b>"
        )

        update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching price data: {e}")
