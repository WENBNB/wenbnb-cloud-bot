# WENBNB Cloud Bot (V1)
# Confidential Prototype â€” Stage 1 Build

# Fix for imghdr module on newer Python versions
try:
    import imghdr
except ModuleNotFoundError:
    import mimetypes
    class imghdr:
        @staticmethod
        def what(filename):
            t = mimetypes.guess_type(filename)[0]
            if t and "image" in t:
                return t.split("/")[-1]
            return None


import os, logging, sqlite3, glob, importlib
from telegram.ext import Updater, CommandHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY") or ""
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS") or "0x0000000000000000000000000000000000000000"
OWNER_ID = int(os.getenv("OWNER_ID") or 0)
DB_FILE = os.getenv("DB_FILE") or "wenbot.db"

if not TELEGRAM_TOKEN:
    raise SystemExit("Please set TELEGRAM_TOKEN in environment variables.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("WENBNBCloudBot")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS giveaways (id INTEGER PRIMARY KEY, chat_id INTEGER, message_id INTEGER, entrants TEXT, active INTEGER DEFAULT 1, created_at INTEGER)''')
conn.commit()

def start(update, context):
    name = update.effective_user.first_name or "anon"
    update.message.reply_text(f"ðŸ”¥ Welcome {name}! Iâ€™m WENBNB Bot ðŸ¤– â€” Type /help for commands.")

def help_cmd(update, context):
    txt = (
        "/meme <topic> - Generate meme caption\n"
        "/price - Show BNB price\n"
        "/tokeninfo - Token supply & stats\n"
        "/airdropcheck <wallet> - Check airdrop eligibility\n"
        "/giveaway_start - Admin only\n"
        "/giveaway_end - Admin only\n"
    )
    update.message.reply_text(txt)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))

    for path in sorted(glob.glob("plugins/*.py")):
        name = os.path.basename(path)[:-3]
        try:
            mod = importlib.import_module(f"plugins.{name}")
            if hasattr(mod, "register"):
                mod.register(dp, {"conn": conn, "cur": cur, "logger": logger,
                                  "BSCSCAN_API_KEY": BSCSCAN_API_KEY,
                                  "OPENAI_API_KEY": OPENAI_API_KEY,
                                  "WEN_TOKEN_ADDRESS": WEN_TOKEN_ADDRESS,
                                  "OWNER_ID": OWNER_ID})
                logger.info("Loaded plugin %s", name)
        except Exception as e:
            logger.exception("Plugin load failed: %s", e)

    updater.start_polling()
    logger.info("WENBNB Cloud Bot started.")
    updater.idle()

if __name__ == "__main__":
    main()


