import openai
from telegram import Update
from telegram.ext import CallbackContext

# 🌐 Auto AI Chat System — WENBNB Neural Engine
def ai_auto_reply(update: Update, context: CallbackContext):
    user_message = update.message.text.strip()
    user_name = update.effective_user.first_name or "friend"

    # Skip system commands (so it doesn’t reply to /help or /start)
    if user_message.startswith("/"):
        return

    try:
        # Typing indicator
        update.message.chat.send_action("typing")

        # 🤖 AI Engine processing
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are WENBNB Neural Engine — an advanced AI from the Web3 ecosystem, expert in crypto, blockchain, and memes. Always respond helpfully, with personality."},
                {"role": "user", "content": user_message}
            ],
        )

        reply = response.choices[0].message["content"]

        # ✨ Reply with AI touch
        formatted = (
            f"💬 <b>Neural Insight:</b>\n"
            f"{reply}\n\n"
            "🚀 <i>Powered by WENBNB Neural Engine — AI Core Intelligence 24×7</i>"
        )

        update.message.reply_text(formatted, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Engine Error:\n{e}")
