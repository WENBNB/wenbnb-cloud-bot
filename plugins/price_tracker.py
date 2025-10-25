from telegram.ext import CommandHandler
import requests, html, random, math, os, re

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Intelligence v5.7.2 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
BSCSCAN_VERIFY = "https://api.bscscan.com/api?module=contract&action=getsourcecode&address={addr}&apikey={api}"

# === Config ===
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
DEFAULT_TOKEN = "wenbnb"

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

def neural_rank(L, V):
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

def verify_contract(address: str):
    if not address or not BSCSCAN_API_KEY:
        return "⚙️ Verification unavailable"
    try:
        res = requests.get(BSCSCAN_VERIFY.format(addr=address, api=BSCSCAN_API_KEY), timeout=10).json()
        if res.get("status") == "1":
            if res.get("result", [{}])[0].get("SourceCode"):
                return "✅ Verified Source"
        return "⚠️ Unable to verify contract"
    except Exception:
        return "⚙️ Verification check failed"

def strict_token_match(pairs, query):
    """Smarter filtering — matches symbol/name/address, skips ETH noise."""
    qlow = query.lower()
    ignore = {"eth", "weth", "usdt", "usdc", "bnb", "busd"}
    exact_match, fallback = None, None
    for p in pairs:
        base = p.get("baseToken", {})
        sym = (base.get("symbol") or "").lower()
        name = (base.get("name") or "").lower()
        addr = (base.get("address") or "").lower()
        if sym in ignore or name in ignore:
            continue
        if qlow == sym or qlow == name or qlow == addr:
            exact_match = p
            break
        if qlow in sym or qlow in name:
            fallback = p
    return exact_match or fallback or (pairs[0] if pairs else None)

def is_contract_address(q: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", q.strip()))

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        token = context.args[0].lower() if context.args else DEFAULT_TOKEN
        if not context.args:
            update.message.reply_text(
                f"💡 No token specified — showing default market data for <b>{DEFAULT_TOKEN.upper()}</b>.",
                parse_mode="HTML"
            )

        try:
            bnb_price = float(requests.get(BINANCE_BNB, timeout=10).json().get("price", 0))
        except Exception:
            bnb_price = 0

        token_name, token_symbol, token_price = token, "", None
        chain, liquidity, volume24, nmr = "Unknown", 0, 0, "N/A"
        dex_source, verify_status = "CoinGecko", ""

        # === 1️⃣ CoinGecko primary lookup ===
        try:
            cg = requests.get(COINGECKO_SIMPLE.format(id=token), timeout=10).json()
            token_price = cg.get(token, {}).get("usd")
        except Exception:
            token_price = None

        # === 2️⃣ DexScreener smart match fallback ===
        if not token_price:
            try:
                query_target = token
                if token == DEFAULT_TOKEN and WEN_TOKEN_ADDRESS:
                    query_target = WEN_TOKEN_ADDRESS
                data = requests.get(DEXSCREENER_SEARCH.format(q=query_target), timeout=10).json()
                pairs = data.get("pairs", [])

                # 🧠 Smart Match Logic
                if is_contract_address(query_target):
                    # Look for contract-based match only
                    match = next((p for p in pairs if (p.get("baseToken", {}).get("address", "").lower() == query_target.lower())), None)
                else:
                    match = strict_token_match(pairs, query_target)

                if match:
                    base = match.get("baseToken", {})
                    token_name = base.get("name") or base.get("symbol") or token
                    token_symbol = base.get("symbol") or token.upper()
                    token_price = match.get("priceUsd", "N/A")
                    dex_source = match.get("dexId", "Unknown DEX").capitalize()
                    chain = detect_chain(dex_source)
                    liquidity = match.get("liquidity", {}).get("usd", 0)
                    volume24 = match.get("volume", {}).get("h24", 0)
                    nmr = neural_rank(liquidity, volume24)
                    token_addr = base.get("address") or ""
                    if token_addr:
                        verify_status = verify_contract(token_addr)
            except Exception:
                token_price, dex_source = "N/A", "Not Found"

        # === Insight Engine ===
        insights = [
            f"{token_name} shows <b>healthy flow</b> 💎",
            f"{token_name} is <b>cooling off slightly</b> 🪶",
            f"{token_name} looks <b>volatile</b> — watch carefully ⚡",
            f"{token_name} heating up on {chain} 🔥",
            f"{token_name} attracting <b>smart traders</b> 🧠"
        ]
        insight = random.choice(insights)

        # === Message Output ===
        msg = (
            f"💹 <b>WENBNB Market Feed</b>\n\n"
            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"🔥 <b>BNB:</b> ${short_float(bnb_price)}\n"
            f"📈 <i>Data Source:</i> {dex_source}\n"
        )
        if verify_status:
            msg += f"🛡️ <b>Verification:</b> {verify_status}\n"
        msg += (
            f"\n🧠 Insight: <b>{insight}</b>\n\n"
            f"{BRAND_FOOTER}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v5.7.2 Neural SmartMatch Edition)")
