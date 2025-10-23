# plugins/help_ai.py
"""
WENBNB AI Help System v4.0 — Interactive Smart Guide
Locked & Approved — Emotion-Aware Context Mode
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# === CORE HELP MESSAGE ===

def help_ai(update: Update, context: CallbackContext):
    """Main interactive help system"""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("💰 Token & Price", callback_data="help_token"),
            InlineKeyboardButton("🎁 Airdrops", callback_data="help_airdrop")
        ],
        [
            InlineKeyboardButton("😂 Meme Generator", callback_data="help_meme"),
            InlineKeyboardButton("🧠 AI Analysis", callback_data="help_ai_analyze")
        ],
        [
            InlineKeyboardButton("🔗 Web3 Connect", callback_data="help_web3"),
            InlineKeyboardButton("🎉 Giveaways", callback_data="help_giveaway")
        ],
        [
            InlineKeyboardButton("⚙️ Admin Tools", callback_data="help_admin"),
            InlineKeyboardButton("💬 About WENBNB", callback_data="help_about")
        ]
    ]

    text = (
        f"👋 <b>Welcome {user.first_name or 'User'}!</b>\n\n"
        "I'm your <b>WENBNB Neural Assistant</b> — a smart, blockchain-aware AI system here to guide you through every command.\n\n"
        "✨ <b>Choose a topic below to learn more:</b>\n"
        f"{BRAND_FOOTER}"
    )

    update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


# === CALLBACK HANDLERS ===

def help_callback(update: Update, context: CallbackContext):
    """Handles each button help section"""
    query = update.callback_query
    data = query.data

    responses = {
        "help_token": (
            "💰 <b>Token & Price Commands</b>\n\n"
            "Use <code>/tokeninfo</code> to get full WENBNB token stats.\n"
            "Use <code>/price</code> to check real-time BNB & WENBNB prices.\n"
            "Supports Coingecko + Binance APIs.\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_airdrop": (
            "🎁 <b>Airdrop Checker</b>\n\n"
            "Command: <code>/airdropcheck</code>\n"
            "→ Enter your wallet to check eligibility instantly.\n"
            "→ Works with AI + Web3 sync for real validation.\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_meme": (
            "😂 <b>AI Meme Generator</b>\n\n"
            "Command: <code>/meme</code>\n"
            "→ Generates unique memes using neural creativity.\n"
            "→ You can send text, or let AI create one for you!\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_ai_analyze": (
            "🧠 <b>AI Analysis Mode</b>\n\n"
            "Command: <code>/aianalyze</code>\n"
            "→ Type any question, and AI replies in context.\n"
            "→ Supports emotional tone + adaptive replies.\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_web3": (
            "🔗 <b>Web3 Connection Tools</b>\n\n"
            "Commands:\n"
            "• <code>/connect &lt;wallet&gt;</code> — link your wallet\n"
            "• <code>/wallet</code> — view wallet info\n"
            "• <code>/track &lt;contract&gt;</code> — live token tracking\n"
            "• <code>/disconnect</code> — unlink wallet\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_giveaway": (
            "🎉 <b>Giveaway System</b>\n\n"
            "Commands:\n"
            "• <code>/giveaway_start</code> — begin event (admin only)\n"
            "• <code>/giveaway_end</code> — end & pick winner\n"
            "• Smart random selection + fairness tracking.\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_admin": (
            "⚙️ <b>Admin Tools</b>\n\n"
            "Command: <code>/admin</code>\n"
            "→ Opens Neural Admin Panel\n"
            "→ Real-time user stats, AI queries, and token logs.\n"
            "→ Includes Refresh, Reset, and Broadcast tools.\n\n"
            f"{BRAND_FOOTER}"
        ),
        "help_about": (
            "💫 <b>About WENBNB Neural Engine</b>\n\n"
            "An AI-Blockchain fusion bot powered by smart APIs, Web3 connectivity, and adaptive memory.\n\n"
            "🧠 Modules include:\n"
            "• Token Intelligence\n"
            "• Airdrop Checker\n"
            "• Meme AI\n"
            "• Web3 Connect\n"
            "• Neural Admin Panel\n"
            "• Emotion-Aware Reply Engine\n\n"
            "✨ Designed for next-gen communities.\n\n"
            f"{BRAND_FOOTER}"
        ),
    }

    response_text = responses.get(data, "❓ Unknown option. Please try again.")
    query.edit_message_text(response_text, parse_mode="HTML")


# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("help", help_ai))
    dp.add_handler(CallbackQueryHandler(help_callback, pattern="help_"))
