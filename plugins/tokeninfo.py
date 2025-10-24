from telegram.ext import CommandHandler
from telegram import Update
import requests, html, os, math

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Token Intelligence v8.1 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"

# === Utils ===
def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id: str) -> str:
    dex_id = (dex_id or "").lower()
    if "pancake" in dex_id: return "BSC"
    if "uniswap" in dex_id: return "Ethereum"
    if "base" in dex_id: return "Base"
    if "arbitrum" in dex_id: return "Arbitrum"
    if "solana" in dex_id: return "Solana"
    return "Unknown"

def neural_token_rank(liquidity_usd: float, volume24_usd: float) -> str:
    """AI-like token score based on liquidity & volume."""
    try:
        L = max(1.0, float(liquidity_usd))
        V = max(1.0, float(volume24_usd))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except Exception:
        return "N/A"

# === /tokeninfo Command ===
def tokeninfo_cmd(update: Update, context):
    chat_id = update.effective_chat.id
    args = context.args
    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # 🧠 Default fallback: if no token specified, use WENBNB
    if not args:
        query = "wenbnb"
        update.message.reply_text(
            "💡 No token specified — showing default token <b>WENBNB</b> data.",
            parse_mode="HTML"
        )
    else:
        query = args[0].strip()

    try:
        # --- Detect if it's a contract address ---
        r = requests.get(DEXSCREENER_SEARCH.format(q=query), timeout=10)
        data = r.json()
        pairs = data.get("pairs", [])
        result = None

        if pairs:
            qlow = query.lower()
            for p in pairs:
                base = p.get("baseToken", {})
                sym = (base.get("symbol") or "").lower()
                name = (base.get("name") or "").lower()
                addr = (base.get("address") or "").lower()
                if qlow in [sym, name, addr]:
                    result = p
                    break
            if not result:
                result = pairs[0]

        if not result:
            update.message.reply_text(
                f"❌ Could not find token on DexScreener for '<b>{html.escape(query)}</b>'.\n"
                f"Try using the contract address or another symbol.",
                parse_mode="HTML"
            )
            return

        # --- Extract info ---
        base = result.get("baseToken", {})
        pair_name = result.get("pairName", "N/A")
        price_usd = result.get("priceUsd", "N/A")
        dex = result.get("dexId", "DEX").capitalize()
        liquidity = result.get("liquidity", {}).get("usd", 0)
        volume24 = result.get("volume", {}).get("h24", 0)
        pair_url = result.get("url") or ""
        token_name = base.get("name") or base.get("symbol") or "Unknown"
        token_symbol = base.get("symbol") or ""
        token_address = base.get("address") or ""

        # --- Detect chain & Neural Rank ---
        chain = detect_chain(dex)
        rank = neural_token_rank(liquidity, volume24)

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
        lines = [
            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>",
            f"🌐 <b>Chain:</b> {chain}",
            f"🏦 <b>DEX:</b> {dex}",
        ]
        if token_address:
            lines.append(f"🔗 <b>Contract:</b> <code>{token_address}</code>")
        lines.append(f"💰 <b>Price:</b> ${short_float(price_usd)}")
        if cg_price:
            lines.append(f"💱 <b>CoinGecko:</b> ${short_float(cg_price)}")
        lines.append(f"💧 <b>Liquidity:</b> ${short_float(liquidity)}")
        lines.append(f"📊 <b>24h Volume:</b> ${short_float(volume24)}")
        lines.append(f"🏅 <b>Neural Token Rank:</b> {rank}")

        if pair_url:
            lines.append(f"🌐 <a href=\"{pair_url}\">View Pair on DexScreener</a>")
        lines.append("")
        lines.append(f"🧠 Insight: {token_symbol or token_name} active on {chain} — monitored by Neural Intelligence ⚙️")
        lines.append("")
        lines.append(BRAND_FOOTER)

        reply = "\n".join(lines)
        update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=False)

    except Exception as e:
        print("Error in tokeninfo_cmd:", e)
        update.message.reply_text(
            "⚙️ Neural Engine temporarily syncing... please retry soon.",
            parse_mode="HTML"
        )

# === Register Command ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
    print("✅ Loaded plugin: plugins.tokeninfo (v8.1 Neural Rank Edition)")
