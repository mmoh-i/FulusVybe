import os
import requests
import threading
import queue
import time
import json
import websocket
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File handler for WebSocket messages
file_handler = logging.FileHandler('websocket_messages.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(file_handler)

# API Keys and Configuration
VYBE_API_KEY = os.getenv("VYBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
VYBE_API_BASE_URL = os.getenv("VYBE_API_BASE_URL")

# Proxy configuration for PythonAnywhere
PROXY = {
    "http": "http://proxy.server:3128",
    "https": "http://proxy.server:3128"
}

# DEX program IDs
DEX_PROGRAM_IDS = {
    "orca": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
    "raydium": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "meteora": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
    "phoenix": "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",
    "pumpfun": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
}

# State class to hold wallet data
class WalletState:
    def __init__(self):
        self.wallet_address = ""
        self.token_balances = {}
        self.historical_balances = {}
        self.nft_balances = {}
        self.insights = ""

# Navigation buttons
def get_nav_buttons():
    return [
        [
            InlineKeyboardButton("🏠 Home", callback_data="home"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ]
    ]

# Fetch wallet data from Vybe API endpoints with retry
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_wallet_data(wallet_address):
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    proxies = PROXY if os.getenv("PYTHONANYWHERE") == "true" else None
    data = {
        "token_balances": {},
        "historical_balances": {},
        "nft_balances": {}
    }

    try:
        url = f"{VYBE_API_BASE_URL}/account/token-balance/{wallet_address}"
        response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
        response.raise_for_status()
        data["token_balances"] = response.json()
    except requests.RequestException as e:
        logger.error(f"Token balance fetch failed: {e}")
        data["token_balances"] = {"error": "Network issue, please try again later"}

    try:
        url = f"{VYBE_API_BASE_URL}/account/token-balance-ts/{wallet_address}"
        response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
        response.raise_for_status()
        data["historical_balances"] = response.json()
    except requests.RequestException as e:
        logger.error(f"Historical balance fetch failed: {e}")
        data["historical_balances"] = {"error": "Network issue, please try again later"}

    try:
        url = f"{VYBE_API_BASE_URL}/account/nft-balance/{wallet_address}"
        response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
        response.raise_for_status()
        data["nft_balances"] = response.json()
    except requests.RequestException as e:
        logger.error(f"NFT balance fetch failed: {e}")
        data["nft_balances"] = {"error": "Network issue, please try again later"}

    return data

# Fetch token holders time series
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_token_holders(token_mint):
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    proxies = PROXY if os.getenv("PYTHONANYWHERE") == "true" else None
    url = f"{VYBE_API_BASE_URL}/token/{token_mint}/holders-ts?days=30"
    response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
    response.raise_for_status()
    return response.json()

# Fetch list of tokens
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_tokens():
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    proxies = PROXY if os.getenv("PYTHONANYWHERE") == "true" else None
    url = f"{VYBE_API_BASE_URL}/tokens"
    response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
    response.raise_for_status()
    return response.json()

# Generate humorous insights with Groq
def generate_insights(state: WalletState):
    token_balances = state.token_balances
    historical_balances = state.historical_balances
    nft_balances = state.nft_balances

    balance_summary = "No token data—your wallet's on a diet!"
    if "error" not in token_balances and token_balances.get("data"):
        balance_summary = "\n".join(
            [f"{token.get('symbol', 'Unknown')}: {token.get('amount', 0)} (Value: ${token.get('valueUsd', 0)})"
             for token in token_balances["data"]]
        )

    historical_summary = "No historical data—time travel isn't your thing yet."
    if "error" not in historical_balances and historical_balances.get("data"):
        historical_data = historical_balances["data"]
        if len(historical_data) >= 2:
            initial_value = float(historical_data[0].get("systemValue", 0))
            final_value = float(historical_data[-1].get("systemValue", 0))
            value_change = final_value - initial_value
            historical_summary = f"Portfolio value changed by ${value_change:.2f}—up, down, or sideways?"

    nft_summary = "No NFTs—you're not cool enough for digital art."
    if "error" not in nft_balances and nft_balances.get("data") is not None:
        nft_count = len(nft_balances["data"])
        nft_summary = f"NFT Holdings: {nft_count} NFTs (Total Value: ${nft_balances.get('totalUsd', '0')})"

    full_summary = f"""
    Current Token Holdings:
    {balance_summary}

    Historical Performance:
    {historical_summary}

    {nft_summary}
    """

    prompt_template = PromptTemplate(
        input_variables=["full_summary"],
        template="Analyze this wallet data and give me some hilarious investment insights (keep it funny, max 3 sentences):\n{full_summary}\nEnd with: 'Craving more wallet wisdom? Hit up Vybe at https://vybe.fyi!'"
    )

    try:
        groq = ChatGroq(api_key=GROK_API_KEY, model_name="llama3-8b-8192")
        insights = groq.invoke(prompt_template.format(full_summary=full_summary)).content
        state.insights = insights
    except Exception as e:
        state.insights = f"Insights machine broke: {str(e)}—guess you're too boring to analyze! Craving more wallet wisdom? Hit up Vybe at https://vybe.fyi!"
    return state

# Fetch program active users time series
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_program_active_users(program_address):
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    proxies = PROXY if os.getenv("PYTHONANYWHERE") == "true" else None
    url = f"{VYBE_API_BASE_URL}/program/{program_address}/active-users-ts"
    response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
    response.raise_for_status()
    return response.json()

# Fetch recent token trades
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_token_trades():
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    proxies = PROXY if os.getenv("PYTHONANYWHERE") == "true" else None
    url = f"{VYBE_API_BASE_URL}/token/trades"
    response = requests.get(url, headers=headers, timeout=30, proxies=proxies)
    response.raise_for_status()
    return response.json()

# Format a transaction for display
def format_transaction(tx):
    try:
        data = tx.get('data', tx)
        # Handle nested data structures
        if isinstance(data, dict):
            mint = data.get('mintAddress') or data.get('mint') or 'N/A'
            amount = float(data.get('amount', 0)) / (10 ** data.get('decimal', 1)) if data.get('amount') and data.get('decimal') else 0.0
            sender = data.get('senderAddress') or data.get('sender') or 'N/A'
            receiver = data.get('receiverAddress') or data.get('receiver') or 'N/A'
            block_time = data.get('blockTime') or data.get('timestamp') or 0
            signature = data.get('signature') or data.get('txId') or 'N/A'
        else:
            return None

        token = mint[:8] + '...' if mint != 'N/A' else 'N/A'
        sender = sender[:8] + '...' if sender != 'N/A' else 'N/A'
        receiver = receiver[:8] + '...' if receiver != 'N/A' else 'N/A'
        timestamp = datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S') if block_time else 'N/A'
        signature = signature[:8] + '...' if signature != 'N/A' else 'N/A'
        return f"Token: {token}, Amount: {amount:.4f}, From: {sender}, To: {receiver}, Time: {timestamp}, Tx: {signature}"
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Failed to format transaction: {e}, Raw: {json.dumps(tx, indent=2)}")
        return None

# WebSocket client for live data
live_transactions = []
live_lock = threading.Lock()
dex_queue = queue.Queue()

def run_websocket():
    # Check if running on PythonAnywhere
    if os.getenv("PYTHONANYWHERE") == "true":
        logger.info("WebSocket disabled on PythonAnywhere due to proxy restrictions")
        return

    def on_message(ws, message):
        try:
            data = json.loads(message)
            logger.debug(f"Raw WebSocket message: {json.dumps(data, indent=2)}")
            
            # Handle DEX-specific message formats
            program_id = data.get('data', {}).get('programId')
            if program_id in DEX_PROGRAM_IDS.values():
                # Handle trades from all DEXs
                trade_data = data.get('data', {})
                if trade_data.get('type') == 'trade':
                    with live_lock:
                        live_transactions.append(data)
                        if len(live_transactions) > 100:
                            live_transactions.pop(0)
            # Handle other message types
            elif (data.get('signature') or data.get('mintAddress') or
                  data.get('data', {}).get('signature') or data.get('data', {}).get('mintAddress') or
                  data.get('txId') or data.get('mint')):
                with live_lock:
                    live_transactions.append(data)
                    if len(live_transactions) > 100:
                        live_transactions.pop(0)
        except json.JSONDecodeError:
            logger.warning("Received invalid JSON message")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    def on_error(ws, error):
        logger.error(f"WebSocket error: {error}")
        # Attempt to reconnect after a delay
        time.sleep(5)
        run_websocket()

    def on_open(ws):
        logger.info("Connected to Vybe live endpoint")
        while True:
            try:
                dex = dex_queue.get_nowait()
                if dex in DEX_PROGRAM_IDS:
                    program_id = DEX_PROGRAM_IDS[dex]
                    config = {
                        "type": "configure",
                        "filters": {
                            "trades": [
                                {
                                    "programId": program_id,
                                    "marketId": "*"  # Allow all markets for all DEXs
                                }
                            ],
                            "transfers": [],
                            "oraclePrices": []
                        }
                    }
                    ws.send(json.dumps(config))
                    logger.info(f"Sent configuration for {dex}: {config}")
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Failed to send configuration: {e}")

    def on_close(ws, close_status_code, close_msg):
        logger.info(f"WebSocket closed: {close_status_code}, {close_msg}")
        # Attempt to reconnect after a delay
        time.sleep(5)
        run_websocket()

    headers = {"x-api-key": VYBE_API_KEY}
    ws = websocket.WebSocketApp(
        "wss://api.vybenetwork.xyz/live",
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("💼 Wallet Tools", callback_data="wallet"),
            InlineKeyboardButton("📊 Token Info", callback_data="tokens"),
        ],
        [
            InlineKeyboardButton("💸 Trades", callback_data="trades"),
            InlineKeyboardButton("ℹ️ All Commands", callback_data="commands"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Yo, pick your vibe! 🚀 Dive into wallets, tokens, or live trades with Vybe's epic API.",
        reply_markup=reply_markup
    )

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🔍 Analyze Wallet", callback_data="analyze_prompt"),
        ],
        get_nav_buttons()[0]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "💼 **Wallet Tools**:\nPick an action to roast your wallet!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🪙 List Tokens", callback_data="tokens_list"),
            InlineKeyboardButton("📈 Token Price", callback_data="price_prompt"),
        ],
        [
            InlineKeyboardButton("👥 Token Holders", callback_data="holders_prompt"),
        ],
        get_nav_buttons()[0]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "📊 **Token Info**:\nExplore tokens on Solana!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def trades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the query if it exists
    query = update.callback_query
    
    # Answer the callback query if it exists
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    keyboard = [
        [
            InlineKeyboardButton("🔥 Live Trades", callback_data="live"),
            InlineKeyboardButton("📜 Recent Trades", callback_data="token_trades"),
        ],
        [
            InlineKeyboardButton("📉 Program Trends", callback_data="trends_prompt"),
        ],
        get_nav_buttons()[0]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
        "💸 <b>Trades</b>:\nCatch the action on Solana DEXs!",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    response = (
        "**All Commands**:\n"
        "💼 /wallet - Wallet tools (analyze, etc.)\n"
        "📊 /tokens - Token info (list, price, holders)\n"
        "💸 /trades - Trade data (live, recent, trends)\n"
        "ℹ️ Want the full scoop? Hit up Vybe at https://vybe.fyi!"
    )
    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        response,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def analyze_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting'] = 'analyze'
    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "🔍 Gimme a wallet address to roast! (e.g., /analyze 88QegP3WTisgqm8sfjcGqcFVYqXZ3wXnERGNHBMuTBJu)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def price_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting'] = 'price'
    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "📈 Drop a token mint address for price history! (e.g., /price So11111111111111111111111111111111111111112)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def trends_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting'] = 'trends'
    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "📉 Enter a program address for user trends! (e.g., /program_trends 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def holders_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting'] = 'holders'
    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "👥 Need a token mint address for holder stats! (e.g., /token_holders So11111111111111111111111111111111111111112)",
        reply_markup=reply_markup
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Yo, give me a wallet address: /analyze <address>",
            reply_markup=reply_markup
        )
        return

    wallet_address = context.args[0]
    state = WalletState()
    state.wallet_address = wallet_address

    try:
        result = fetch_wallet_data(wallet_address)
        state.token_balances = result["token_balances"]
        state.historical_balances = result["historical_balances"]
        state.nft_balances = result["nft_balances"]
        state = generate_insights(state)

        response = f"**Wallet Roast for: {wallet_address}**\n\n"

        if "error" not in result["token_balances"]:
            if result["token_balances"].get("data"):
                balances = result["token_balances"]["data"]
                response += "**Current Token Holdings**\n"
                response += "\n".join([f"{token.get('symbol', 'Unknown')}: {token.get('amount', 0)} (${token.get('valueUsd', 0)})" for token in balances]) + "\n"
                response += "Craving token analytics? Check Vybe: https://vybe.fyi\n\n"
            else:
                response += "**Current Token Holdings**\nNo tokens found—are you a minimalist or just broke?\n\n"
        else:
            response += "**Current Token Holdings**\nConnection hiccup—Vybe's servers are playing hide and seek!\n\n"

        if "error" not in result["historical_balances"] and result["historical_balances"].get("data"):
            historical_data = result["historical_balances"]["data"]
            if len(historical_data) >= 2:
                initial_value = float(historical_data[0].get("systemValue", 0))
                final_value = float(historical_data[-1].get("systemValue", 0))
                value_change = final_value - initial_value
                response += f"**Portfolio Value Change**: ${value_change:.2f}—did you sneeze and miss it?\n"
                response += "See trends on Vybe: https://vybe.fyi\n\n"
            else:
                response += "**Portfolio Value Change**\nNo history to spill—your wallet's a blank slate!\n\n"
        else:
            response += "**Portfolio Value Change**\nNo history to spill—your wallet's a blank slate!\n\n"

        if "error" not in result["nft_balances"] and result["nft_balances"].get("data") is not None:
            nft_count = len(result["nft_balances"]["data"])
            response += f"**NFT Holdings**: {nft_count} NFTs (Total Value: ${result['nft_balances'].get('totalUsd', '0')})\n"
            response += "Explore NFTs on Vybe: https://vybe.fyi\n\n"
        else:
            response += "**NFT Holdings**\nNo NFTs—guess you're not into digital bling yet!\n\n"

        response += f"**Hot Takes**\n{state.insights}"
    except Exception as e:
        response = f"Oops, something broke: {str(e)}—try again!\nFor more, visit Vybe: https://vybe.fyi"
        keyboard = [
            [InlineKeyboardButton("🔄 Retry", callback_data="analyze_prompt")],
            get_nav_buttons()[0]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        return

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Need a token mint address: /price <token_mint>",
            reply_markup=reply_markup
        )
        return

    token_mint = context.args[0]
    headers = {"accept": "application/json", "X-API-KEY": VYBE_API_KEY}
    try:
        url = f"{VYBE_API_BASE_URL}/token/price-history/{token_mint}?days=30"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            response_text = (
                f"Token {token_mint[:8]}... not found on Vybe.\n"
                "This could mean:\n"
                "1. The token is too new\n"
                "2. The token hasn't been traded yet\n"
                "3. The token mint address is incorrect\n\n"
                "Try checking the token on Vybe: https://vybe.fyi"
            )
        elif response.status_code != 200:
            response_text = (
                f"Vybe API returned error {response.status_code}\n"
                "Please try again later or check Vybe: https://vybe.fyi"
            )
        else:
            data = response.json()
            if not data.get("data"):
                response_text = "No price data found—check Vybe for more: https://vybe.fyi"
            else:
                prices = data["data"]
                if not prices:
                    response_text = "No price history available for this token yet"
                else:
                    latest_price = prices[-1]['priceUsd']
                    max_price = max(p['priceUsd'] for p in prices)
                    min_price = min(p['priceUsd'] for p in prices)
                    response_text = (
                        f"<b>30-day Price History for {token_mint[:8]}...</b>\n"
                        f"Latest: ${latest_price:.6f}\n"
                        f"Max: ${max_price:.6f}\n"
                        f"Min: ${min_price:.6f}\n"
                        f"More on Vybe: https://vybe.fyi"
                    )
    except requests.RequestException as e:
        response_text = (
            f"Could not fetch price data: {str(e)}\n"
            "Please try again later or check Vybe: https://vybe.fyi"
        )
    except Exception as e:
        response_text = (
            f"An unexpected error occurred: {str(e)}\n"
            "Please try again later or check Vybe: https://vybe.fyi"
        )

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response_text, reply_markup=reply_markup, parse_mode="HTML")

async def program_trends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Need a program address: /program_trends <program_address>",
            reply_markup=reply_markup
        )
        return
    program_address = context.args[0]
    try:
        data = fetch_program_active_users(program_address)
        if "error" in data:
            response = f"Failed to fetch trends—try Vybe: https://vybe.fyi"
        else:
            trends = data.get("data", [])
            if trends:
                response = (
                    f"Active users for {program_address[:8]}... (last 7 days): {', '.join([str(t.get('activeUsers', 0)) for t in trends[-7:]])}"
                    f"\nDetailed trends on Vybe: https://vybe.fyi"
                )
            else:
                response = "No data for this program—try Vybe: https://vybe.fyi"
    except Exception as e:
        response = f"Oops, something broke: {str(e)}—try again!\nFor more, visit Vybe: https://vybe.fyi"
        keyboard = [
            [InlineKeyboardButton("🔄 Retry", callback_data="trends_prompt")],
            get_nav_buttons()[0]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)
        return

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

async def token_trades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the query if it exists
    query = update.callback_query
    
    # Answer the callback query if it exists
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    try:
        data = fetch_token_trades()
        if "error" in data:
            response = "Failed to fetch trades—try Vybe: https://vybe.fyi"
        else:
            trades = data.get("data", [])[:3]
            if trades:
                response = (
                    "<b>Recent Trades</b>\n" +
                    "\n".join([f"{t['baseMintAddress'][:8]}... for {t['quoteSize']} SOL at ${t['price']}" for t in trades]) +
                    "\nFor a comprehensive list, visit Vybe: https://vybe.fyi"
                )
            else:
                response = "No trades found—check Vybe: https://vybe.fyi"
    except Exception as e:
        response = f"Oops, something broke: {str(e)}—try again!\nFor more, visit Vybe: https://vybe.fyi"
        keyboard = [
            [InlineKeyboardButton("🔄 Retry", callback_data="token_trades")],
            get_nav_buttons()[0]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")
        return

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")

async def token_holders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Need a token mint address: /token_holders <token_mint>",
            reply_markup=reply_markup
        )
        return
    token_mint = context.args[0]
    try:
        data = fetch_token_holders(token_mint)
        if "error" in data:
            response = (
                f"Token {token_mint[:8]}... not found on Vybe.\n\n"
                "This could mean:\n"
                "1. The token is too new\n"
                "2. The token hasn't been traded yet\n"
                "3. The token mint address is incorrect\n\n"
                "Try checking the token on Vybe: https://vybe.fyi"
            )
        else:
            holders = data.get("data", [])
            if holders:
                latest = holders[-1]
                timestamp = datetime.utcfromtimestamp(latest['holdersTimestamp']).strftime('%Y-%m-%d')
                response = (
                    f"Token Holders for {token_mint[:8]}... (Last 30 days)\n"
                    f"Latest ({timestamp}): {latest['nHolders']} holders\n"
                )
                if len(holders) > 1:
                    prev = holders[-2]
                    change = latest['nHolders'] - prev['nHolders']
                    response += f"Change: {'+' if change >= 0 else ''}{change} holders\n"
                # Add trend information
                if len(holders) >= 2:
                    first_day = holders[0]['nHolders']
                    last_day = holders[-1]['nHolders']
                    total_change = last_day - first_day
                    response += f"30-day trend: {'+' if total_change >= 0 else ''}{total_change} holders\n"
                response += "More holder stats on Vybe: https://vybe.fyi"
            else:
                response = (
                    f"No holder data found for {token_mint[:8]}...\n\n"
                    "This could mean:\n"
                    "1. The token is too new\n"
                    "2. The token hasn't been traded yet\n"
                    "3. The token mint address is incorrect\n\n"
                    "Try checking the token on Vybe: https://vybe.fyi"
                )
    except Exception as e:
        if "404" in str(e):
            response = (
                f"Token {token_mint[:8]}... not found on Vybe.\n\n"
                "This could mean:\n"
                "1. The token is too new\n"
                "2. The token hasn't been traded yet\n"
                "3. The token mint address is incorrect\n\n"
                "Try checking the token on Vybe: https://vybe.fyi"
            )
        else:
            response = f"An error occurred: {str(e)}\nPlease try again later or check Vybe: https://vybe.fyi"
        keyboard = [
            [InlineKeyboardButton("🔄 Retry", callback_data="holders_prompt")],
            get_nav_buttons()[0]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)
        return

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

async def tokens_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = fetch_tokens()
        if "error" in data:
            response = "Failed to fetch tokens—try Vybe: https://vybe.fyi"
        else:
            tokens = data.get("data", [])[:5]
            if tokens:
                response = "<b>Token List</b>\n"
                for i, token in enumerate(tokens, 1):
                    mint = token.get('mintAddress', 'N/A')[:8] + '...'
                    supply = f"{token.get('currentSupply', 0):,.6f}".rstrip('0').rstrip('.')
                    symbol = token.get('symbol', 'Unknown')
                    name = token.get('name', 'Unknown')
                    response += f"{i}. {symbol} ({name}): {mint} - Supply: {supply}\n"
                response += "See more tokens on Vybe: https://vybe.fyi"
            else:
                response = "No tokens found—check Vybe: https://vybe.fyi"
    except Exception as e:
        response = f"Oops, something broke: {str(e)}—try again!\nFor more, visit Vybe: https://vybe.fyi"
        keyboard = [
            [InlineKeyboardButton("🔄 Retry", callback_data="tokens_list")],
            get_nav_buttons()[0]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)
        return

    keyboard = get_nav_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both message and callback query updates
    if update.callback_query:
        await update.callback_query.message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")

async def live(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    if os.getenv("PYTHONANYWHERE") == "true":
        response = (
            "🚫 Live trades are disabled on PythonAnywhere due to WebSocket restrictions.\n"
            "Please use /token_trades for recent trades or deploy on a platform supporting WebSockets (e.g., Heroku).\n"
            "More info at https://vybe.fyi"
        )
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        return

    keyboard = [
        [
            InlineKeyboardButton("Orca", callback_data="dex_orca"),
            InlineKeyboardButton("Raydium", callback_data="dex_raydium"),
        ],
        [
            InlineKeyboardButton("Meteora", callback_data="dex_meteora"),
            InlineKeyboardButton("Phoenix", callback_data="dex_phoenix"),
        ],
        [
            InlineKeyboardButton("Pump.fun", callback_data="dex_pumpfun"),
        ],
        get_nav_buttons()[0]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
        "🔥 Pick a DEX to view live trades:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "home":
        keyboard = [
            [
                InlineKeyboardButton("💼 Wallet Tools", callback_data="wallet"),
                InlineKeyboardButton("📊 Token Info", callback_data="tokens"),
            ],
            [
                InlineKeyboardButton("💸 Trades", callback_data="trades"),
                InlineKeyboardButton("ℹ️ All Commands", callback_data="commands"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Yo, pick your vibe! 🚀 Dive into wallets, tokens, or live trades with Vybe's epic API.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    if data == "help":
        keyboard = get_nav_buttons()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Need help? Check out Vybe at https://vybe.fyi for the full scoop!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    if data == "wallet":
        await wallet(update, context)
        return

    if data == "tokens":
        await tokens(update, context)
        return

    if data == "trades":
        await trades(update, context)
        return

    if data == "commands":
        await commands(update, context)
        return

    if data == "analyze_prompt":
        await analyze_prompt(update, context)
        return

    if data == "price_prompt":
        await price_prompt(update, context)
        return

    if data == "trends_prompt":
        await trends_prompt(update, context)
        return

    if data == "holders_prompt":
        await holders_prompt(update, context)
        return

    if data == "tokens_list":
        await tokens_list(update, context)
        return

    if data == "token_trades":
        await token_trades(update, context)
        return

    if data == "live":
        await live(update, context)
        return

    if data.startswith("dex_"):
        if os.getenv("PYTHONANYWHERE") == "true":
            response = (
                "🚫 Live trades are disabled on PythonAnywhere due to WebSocket restrictions.\n"
                "Please use /token_trades for recent trades or deploy on a platform supporting WebSockets (e.g., Heroku).\n"
                "More info at https://vybe.fyi"
            )
            keyboard = get_nav_buttons()
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
            return

        dex = data.split("_")[1]
        with live_lock:
            live_transactions.clear()

        dex_queue.put(dex)

        start_time = time.time()
        timeout = 20
        formatted_txs = []

        while time.time() - start_time < timeout and len(formatted_txs) < 3:
            with live_lock:
                transactions = live_transactions[:]
            for tx in transactions:
                formatted = format_transaction(tx)
                if formatted and formatted not in formatted_txs:
                    formatted_txs.append(formatted)
                    if len(formatted_txs) >= 3:
                        break
            if len(formatted_txs) < 3:
                await asyncio.sleep(0.5)

        dex_name = dex.capitalize()
        if formatted_txs:
            summary = "\n".join(formatted_txs)
            response = f"**Live {dex_name} Trades**\n{summary}\nFor more real-time action, visit Vybe: https://vybe.fyi"
            keyboard = [
                [InlineKeyboardButton("↩️ Back to DEXs", callback_data="live")],
                get_nav_buttons()[0]
            ]
        else:
            response = (
                f"No live {dex_name} trades captured yet—try again soon!\n"
                f"Check https://docs.vybenetwork.com/docs/real-time-trades for details.\n"
                f"For more real-time updates, visit Vybe: https://vybe.fyi"
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Retry", callback_data=f"dex_{dex}"),
                 InlineKeyboardButton("↩️ Back to DEXs", callback_data="live")],
                get_nav_buttons()[0]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'awaiting' in context.user_data:
        command = context.user_data['awaiting']
        context.user_data.pop('awaiting')
        if command == 'analyze':
            context.args = [update.message.text]
            await analyze(update, context)
        elif command == 'price':
            context.args = [update.message.text]
            await price(update, context)
        elif command == 'trends':
            context.args = [update.message.text]
            await program_trends(update, context)
        elif command == 'holders':
            context.args = [update.message.text]
            await token_holders(update, context)

def main():
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("wallet", wallet))
    application.add_handler(CommandHandler("tokens", tokens))
    application.add_handler(CommandHandler("trades", trades))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("program_trends", program_trends))
    application.add_handler(CommandHandler("token_trades", token_trades))
    application.add_handler(CommandHandler("token_holders", token_holders))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start WebSocket thread
    ws_thread = threading.Thread(target=run_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()