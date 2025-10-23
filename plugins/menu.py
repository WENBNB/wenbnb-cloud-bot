from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("menu", main_menu))
    dispatcher.add_handler(CallbackQueryHandler(menu_callback))

def main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("💰  Price", callback_data="price"),
            InlineKeyboardButton("📊  Token Info", callback_data="tokeninfo")
        ],
        [
            InlineKeyboardButton("😂  Meme Studio", callback_data="meme"),
            InlineKeyboardButton("🧠  AI Analyze", callback_data="aianalyze")
        ],
        [
            InlineKeyboardButton("🎁  Airdrop Check", callback_data="airdropcheck"),
            InlineKeyboardButton("ℹ️  About", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "✨ *Welcome to WENBNB Neural Engine v5.5*\n\n"
        "Your all-in-one AI + Web3 assistant 🚀\n"
        "_Always online • Powered by AI Cloud 24×7_\n\n"
        "👉 Select a feature below 👇"
    )
    update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    query.answer()

    responses = {
        "price": "💰 Use `/price` to check live BNB + token prices.",
        "tokeninfo": "📊 Try `/tokeninfo wenbnb` for contract details.",
        "meme": "😂 Meme Studio launching soon — stay tuned!",
        "aianalyze": "🧠 Running Neural AI analysis...",
        "airdropcheck": "🎁 Checking airdrop eligibility...",
        "about": "🌐 *WENBNB Neural Engine v5.5*\nAI Core Intelligence 24×7 ☁️"
    }

    query.edit_message_text(responses.get(data, "⚙️ Unknown option."), parse_mode="Markdown")
