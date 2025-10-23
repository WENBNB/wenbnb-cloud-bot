from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("menu", main_menu))
    dispatcher.add_handler(CallbackQueryHandler(menu_callback))

def main_menu(update: Update, context: CallbackContext):
    """Main AI Menu for WENBNB Neural Engine"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Price", callback_data="price"),
            InlineKeyboardButton("📊 Token Info", callback_data="tokeninfo")
        ],
        [
            InlineKeyboardButton("😂 Meme", callback_data="meme"),
            InlineKeyboardButton("🧠 AI Analyze", callback_data="aianalyze")
        ],
        [
            InlineKeyboardButton("🎁 Airdrop Check", callback_data="airdropcheck"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🚀 *Welcome to WENBNB Neural Engine v5.5*\n\n"
        "Your all-in-one AI + Web3 assistant 🤖\n\n"
        "Choose a feature below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def menu_callback(update: Update, context: CallbackContext):
    """Handle Inline Button Actions"""
    query = update.callback_query
    data = query.data
    query.answer()

    responses = {
        "price": "💰 Type `/price` to get live BNB & token prices!",
        "tokeninfo": "📊 Use `/tokeninfo <symbol>` to check any token.",
        "meme": "😂 Meme plugin coming online soon!",
        "aianalyze": "🧠 AI Core Analysis initializing...",
        "airdropcheck": "🎁 Checking your airdrop eligibility...",
        "about": "🌐 Powered by *WENBNB Neural Engine v5.5* — AI Cloud Intelligence 24×7 ☁️"
    }

    query.edit_message_text(
        responses.get(data, "⚙️ Unknown command."),
        parse_mode="Markdown"
    )
