from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext
from threading import Timer
import time

PENDING_VERIFY = {}  # user_id: time stamp
VERIFY_TIMEOUT = 60  # seconds
ADMIN_IDS = [int(os.getenv("OWNER_ID", "0"))]

def send_welcome(update, context, member):
    chat_id = update.effective_chat.id
    uid = member.id
    name = member.first_name

    PENDING_VERIFY[uid] = time.time()

    msg = (
        f"⚡ Welcome {name}!\n"
        f"Real ho to ek 👋 bhejo **{VERIFY_TIMEOUT}s** me.\n"
        f"Bot hue to mummy chappal se peetegi 💀"
    )

    context.bot.send_message(chat_id, msg, parse_mode="Markdown")

    Timer(VERIFY_TIMEOUT, check_kick, args=(context, chat_id, uid, name)).start()


def check_kick(context, chat_id, uid, name):
    if uid in PENDING_VERIFY:
        try:
            context.bot.kick_chat_member(chat_id, uid)
            context.bot.send_message(
                chat_id,
                f"❌ {name} suspect lag raha tha.\n"
                f"Fake vibes = No entry 🚫"
            )
        except:
            pass
        PENDING_VERIFY.pop(uid, None)


def welcome_new_member(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.id in ADMIN_IDS:
            continue  # admins no verify
        send_welcome(update, context, member)


def verify_response(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if uid in PENDING_VERIFY and ("👋" in text or text.lower() in ["hi","hello","yo","hey"]):
        PENDING_VERIFY.pop(uid, None)
        context.bot.send_message(
            chat_id,
            f"✅ Verified! Real banda detected 😌🔥\n"
            f"Chalo ab vibe match karte hain 😏"
        )


def register_handlers(dp, config=None):
    dp.add_handler(
        MessageHandler(Filters.status_update.new_chat_members, welcome_new_member),
        group=3
    )
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, verify_response),
        group=3
    )
