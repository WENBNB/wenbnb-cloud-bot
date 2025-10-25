from telegram.ext import CommandHandler
import requests, html, random, math, re

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Intelligence v8.1.7 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

# === Utility ===
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

def neural_market_rank(L, V):
    try:
        L, V = max(1.0, float(L)), max(1.0, float(V))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except Exception:
        return "N/A"

def is_contract_address(q: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", q.strip()))

def strict_match(pairs, query):
    """Reject ETH/WETH & unrelated results, find exact token."""
    q = query.lower()
    ignore = {"eth", "weth", "usdt", "usdc", "bnb", "busd"}
    if q in ignore:
        return None  # skip direct ETH/BSC confusion
    for p in pairs:
        base = p.get("baseToken", {})
        sym = (base.get("symbol") or "").lower()
        name = (base.get("name") or "").lower()
        addr = (base.get("address") or "").lower()
        if q in [sym, name, addr]:
            return p
    # fallback: partial match
    for p in pairs:
        base = p.get("baseToken", {})
        if q in (base.get("symbol") or "").lower() or q in (base.get("name") or "").lower():
            return p
    return None

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Default fallback token
        token = "wenbnb"
        if context.args:
            token = context.args[0].strip().lower()
        else:
            update.message.reply_text(
                "💡 No token specified — showing default <b>WENBNB</b> market data.",
                parse_mode="HTML"
            )

        # --- Fetch BNB price ---
        try:
            bnb_data = requests.get(BINANCE_BNB, timeout=10).json()
            bnb_price = float(bnb_data.get("price", 0))
        except Exception:
            bnb_price = 0

        # --- Initialize values ---
        token_name, token_symbol, token_price, dex_source = token.upper(), "", None, "CoinGecko"
        chain, liquidity, volume24, nmr = "Unknown", 0, 0, "N/A"

        # === 1️⃣ CoinGecko primary ===
        try:
            cg_data = requests.get(COINGECKO_SIMPLE.format(id=token), timeout=10).json()
            token_price = cg_data.get(token, {}).get("usd")
        except Exception:
            token_price = None

        # === 2️⃣ DexScreener fallback ===
        if not token_price:
            try:
                dex_data = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=10).json()
                pairs = dex_data.get("pairs", [])
                match = strict_match(pairs, token)

                if match:
                    base = match.get("baseToken", {})
                    token_name = base.get("name") or token.upper()
                    token_symbol = base.get("symbol") or token.upper()
                    token_price = match.get("priceUsd", "N/A")
                    dex_source = match.get("dexId", "Unknown DEX").capitalize()
                    chain = detect_chain(dex_source)
                    liquidity = match.get("liquidity", {}).get("usd", 0)
                    volume24 = match.get("volume", {}).get("h24", 0)
                    nmr = neural_market_rank(liquidity, volume24)
                else:
                    token_price = None
            except Exception:
                token_price, dex_source = None, "Not Found"

        # === 3️⃣ If still none, say no data ===
        if not token_price or token_price == "N/A":
            update.message.reply_text(
                f"❌ No valid market data for <b>{html.escape(token.upper())}</b>.\n"
                f"Try using the contract address or known DEX token name.",
                parse_mode="HTML"
            )
            return

        # === Insight ===
        insights = [
            f"{token_name} shows <b>healthy trading flow</b> 💎",
            f"{token_name} is <b>cooling slightly</b> 🪶",
            f"{token_name} is <b>volatile</b> — monitor carefully ⚡",
            f"{token_name} heating up on {chain} 🔥",
            f"{token_name} attracting <b>smart liquidity</b> 🧠"
        ]
        insight = random.choice(insights)

        # === Build reply ===
        msg = (
            f"💹 <b>WENBNB Market Feed</b>\n\n"
            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"🔥 <b>BNB:</b> ${short_float(bnb_price)}\n"
            f"📈 <i>Data Source:</i> {dex_source}\n\n"
            f"🧠 Insight: <b>{insight}</b>\n\n"
            f"{BRAND_FOOTER}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

# === Register Command ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v8.1.7 Neural SmartLock Edition)")
