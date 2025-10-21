import openai
from telegram import Update
from telegram.ext import CallbackContext

def aianalyze(update: Update, context: CallbackContext):
    try:
        user_query = " ".join(context.args) or "Analyze current crypto trends"
        update.message.reply_text("🧠 Neural Engine analyzing... Please wait...")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are WENBNB Neural AI, a crypto data analyst."},
                {"role": "user", "content": user_query}
            ],
        )

        answer = response.choices[0].message["content"]
        update.message.reply_text(f"🤖 AI Insight:\n\n{answer}")

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Engine failed to analyze.\nError: {e}")
