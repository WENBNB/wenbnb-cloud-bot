from telegram.ext import CommandHandler
from telegram import Update
import requests, html, os

BRAND_FOOTER = "🚀 Powered by <b>WENBNB Neural Engine</b> — AI Core Intelligence 24×7 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"

def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def tokeninfo_cmd(update: Update, context):
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        update.message.reply_text(
            "🧠 Usage: /tokeninfo <symbol|contract>\nExample: /tokeninfo wenbnb",
            parse_mode="HTML"
        )
        return

    query = args[0].strip()
    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # --- Detect if it's a contract address ---
        contract = query if query.startswith("0x") else None
        r = requests.get(DEXSCREENER_SEARCH.format(q=query), timeout=10)
        data = r.json()
        pairs = data.get("pairs", [])
        result = None

        if pairs:
            qlow = query.lower()
            # Try to find best match
            for p in pairs:
                base = p.get("baseToken", {})
                sym = (base.get("symbol") or "").lower()
                name = (base.get("name") or "").lower()
                addr = base.get("address") or ""
                if qlow in [sym, name, addr.lower()]:
                    result = p
                    break
            if not result:
                result = pairs[0]

        if not result:
            update.message.reply_text(
                f"❌ Could not find token on DexScreener for '{html.escape(query)}'.\n"
                f"Try using the contract address or another symbol.",
                parse_mode="HTML"
            )
            return

        # --- Extract info ---
        base = result.get("baseToken", {})
        pair_name = result.get("pairName", "N/A")
        price_usd = result.get("priceUsd", "N/A")
        dex = result.get("dexId", "Dex").capitalize()
        liquidity = result.get("liquidity", {}).get("usd", "N/A")
        volume24 = result.get("volume", {}).get("h24", "N/A")
        pair_url = result.get("url") or ""
        token_name = base.get("name") or base.get("symbol") or "Unknown"
        token_symbol = base.get("symbol") or ""
        token_address = base.get("address") or ""

        # --- Try CoinGecko fallback ---
        cg_price = None
        try:
            cg_query = token_symbol.lower() if token_symbol else token_name.lower().replace(" ", "-")
            cg_res = requests.get(COINGECKO_SIMPLE, params={"ids": cg_query, "vs_currencies": "usd"}, timeout=8)
            cg_data = cg_res.json()
            if cg_query in cg_data:
                cg_price = cg_data[cg_query]["usd"]
        except Exception:
            pass

        # --- Build formatted message ---
        lines = []
        lines.append(f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>")
        if token_address:
            lines.append(f"🔗 <b>Contract:</b> <code>{token_address}</code>")
        lines.append(f"💰 <b>Price:</b> ${short_float(price_usd)} ({dex})")
        if cg_price:
            lines.append(f"💱 <b>CoinGecko:</b> ${short_float(cg_price)}")
        if liquidity != "N/A":
            lines.append(f"💧 <b>Liquidity:</b> ${short_float(liquidity)}")
        if volume24 != "N/A":
            lines.append(f"📊 <b>24h Volume:</b> ${short_float(volume24)}")
        if pair_url:
            lines.append(f"🌐 <a href=\"{pair_url}\">View Pair on DexScreener</a>")

        # Add AI-style close
        lines.append("")
        lines.append(
            f"🤖 Smart insight: {token_symbol or token_name} is trending on <b>{dex}</b> — stay alert, {update.effective_user.first_name}! 🚀"
        )
        lines.append("")
        lines.append(BRAND_FOOTER)

        reply = "\n".join(lines)
        update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=False)

    except Exception as e:
        print("Error in tokeninfo_cmd:", e)
        update.message.reply_text(f"⚠️ Internal error. Please try again later.", parse_mode="HTML")

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
    print("✅ Loaded plugin: plugins.tokeninfo")
