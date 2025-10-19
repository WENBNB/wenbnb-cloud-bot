from telegram.ext import CommandHandler
import requests
def register(dispatcher, core):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
def price_cmd(update, context):
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd", timeout=8).json()
        price = r.get("binancecoin", {}).get("usd")
        update.message.reply_text(f"BNB price (USD): ${price}")
    except:
        update.message.reply_text("Price fetch failed.")
