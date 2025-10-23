# plugins/tokeninfo.py
"""
Token info plugin for WENBNB Neural Engine v5.0
Usage:
    /tokeninfo <symbol|contract|name>
Examples:
    /tokeninfo wenbnb
    /tokeninfo 0x12ab...ef34
This plugin tries:
 - DexScreener search (fast) for pairs & token address
 - CoinGecko fallback for price (if available)
 - Provides BscScan link (if we have a BSC contract)
"""
import os
import requests
import html
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"
DEXSCREENER_SEARCH = "https://api.dexscreener.com/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"

def register_handlers(dp):
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd, pass_args=True))

def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def tokeninfo_cmd(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        update.message.reply_text("Usage: /tokeninfo <symbol|contract|name>\nExample: /tokeninfo wenbnb")
        return

    query = args[0].strip()
    update.message.reply_text(f"🔎 Searching token info for: <b>{html.escape(query)}</b>", parse_mode="HTML")

    try:
        # 1) If looks like contract (0x...), form BscScan link and try DexScreener by address
        contract = None
        dex_result = None

        if query.startswith("0x") and len(query) >= 20:
            contract = query
            # try DexScreener search by contract
            r = requests.get(DEXSCREENER_SEARCH.format(q=contract), timeout=12)
            j = r.json()
            pairs = j.get("pairs") or []
            if pairs:
                dex_result = pairs[0]
        else:
            # 2) search DexScreener by symbol/name
            r = requests.get(DEXSCREENER_SEARCH.format(q=query), timeout=12)
            j = r.json()
            pairs = j.get("pairs") or []
            if pairs:
                # try to find exact symbol match first
                dex_result = None
                qlow = query.lower()
                for p in pairs:
                    token = p.get("token") or {}
                    sym = (token.get("symbol") or "").lower()
                    name = (token.get("name") or "").lower()
                    addr = token.get("address") or ""
                    if qlow == sym or qlow == name or qlow in name:
                        dex_result = p
                        break
                # fallback to first pair
                if not dex_result and pairs:
                    dex_result = pairs[0]

        if not dex_result:
            update.message.reply_text(f"❌ Could not find token on DexScreener for '{html.escape(query)}'. Try contract address or another symbol.")
            return

        # Build friendly output
        token = dex_result.get("token", {})
        pair_name = dex_result.get("pairName", "N/A")
        price_usd = dex_result.get("priceUsd", "N/A")
        price_change = dex_result.get("priceChange", "N/A")
        liquidity = dex_result.get("liquidityUsd", "N/A")
        dex = dex_result.get("dexId", "Dex")

        token_name = token.get("name") or token.get("symbol") or pair_name
        token_symbol = token.get("symbol") or ""
        token_address = token.get("address") or ""
        pair_url = dex_result.get("pairUrl") or ""

        # Try CoinGecko as extra price source (best-effort)
        cg_price = None
        try:
            # if we have a symbol, coingecko simple price may help
            cg_query = token_symbol.lower() if token_symbol else token_name.lower().replace(" ", "-")
            cg_r = requests.get(COINGECKO_SIMPLE, params={"ids": cg_query, "vs_currencies": "usd"}, timeout=8)
            cg_j = cg_r.json()
            if cg_query in cg_j:
                cg_price = cg_j[cg_query]["usd"]
        except Exception:
            cg_price = None

        # Format message
        lines = []
        lines.append(f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>")
        if token_address:
            bscscan_link = f"https://bscscan.com/token/{token_address}"
            lines.append(f"🔗 <b>Contract:</b> <a href=\"{bscscan_link}\">{token_address[:8]}...{token_address[-6:]}</a>")
        if price_usd and price_usd != "N/A":
            lines.append(f"💰 <b>Price (DexScreener):</b> ${short_float(price_usd)}")
        if cg_price:
            lines.append(f"💱 <b>Price (CoinGecko):</b> ${short_float(cg_price)}")
        if price_change not in (None, "N/A"):
            try:
                change = float(price_change)
                lines.append(f"📈 <b>24h change:</b> {change:+.2f}%")
            except Exception:
                pass
        if liquidity and liquidity != "N/A":
            try:
                liq = float(liquidity)
                lines.append(f"🧾 <b>Liquidity:</b> ${liq:,.2f}")
            except Exception:
                lines.append(f"🧾 <b>Liquidity:</b> {liquidity}")

        # quick pair info
        if pair_name:
            lines.append(f"🔗 <b>Pair:</b> {html.escape(pair_name)} ({dex})")
        if pair_url:
            lines.append(f"🔎 <b>Pair URL:</b> <a href=\"{pair_url}\">Open Pair</a>")

        # footer & ai hint
        lines.append("")
        lines.append(f"{BRAND_FOOTER}")

        reply = "\n".join(lines)
        update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=False)

    except Exception as e:
        update.message.reply_text(f"⚠️ TokenInfo Error: {e}")
